from typing import Callable, List, Tuple, TypeVar, Optional
from dataclasses import dataclass
import operator
from cytoolz.curried import map, concat, accumulate  # type: ignore
import torch

Tensor = torch.Tensor
Texts = List[str]
Idxs = List[int]
Nlp = Callable[[str], Texts]
A = TypeVar("A", list, Tensor)


@dataclass(init=True)
class SentencizerBase:
  nlp: Nlp
  model: Callable[[Texts], Tensor]
  batch_size: int
  max_sent_length: int
  tol_sent_len: int


class Sentencizer(SentencizerBase):

  def __call__(self, texts: Texts, mode: str = "mmr", *args, **kwargs) -> Texts:

    if mode == "mmr":
      return self.mmr_mode(texts, *args, **kwargs)
    elif mode == "cossim":
      return self.cossim_mode(texts, *args, **kwargs)
    else:
      raise NotImplementedError()

  def cossim_mode(self, texts: Texts, *args, **kwargs) -> Texts:
    text_ids, sents_ids, sents = self.group_data(texts)
    embds: Tensor = self.model(sents)
    batch_sents = self.gather(sents, sents_ids)
    batch_embds = self.gather(embds, sents_ids)

    batch_texts = []

    for i in range(len(batch_sents)):
      text = self.cossim_filter(batch_sents[i], batch_embds[i], **kwargs)
      batch_texts.append(text)

    new_texts = self.gather(batch_texts, text_ids)
    return [*map(lambda text: " ".join(text), new_texts)]

  def mmr_mode(self, texts: Texts, *args, **kwargs):
    text_ids, sents_ids, sents = self.group_data(texts)
    embds: Tensor = self.model(sents)

    batch_sents = self.gather(sents, sents_ids)
    batch_embds = self.gather(embds, sents_ids)

    batch_texts = []

    for i in range(len(batch_sents)):
      text = self.mmr_filter(batch_sents[i], batch_embds[i], **kwargs)
      batch_texts.append(text)

    new_texts = self.gather(batch_texts, text_ids)
    return [*map(lambda text: " ".join(text), new_texts)]

  def mmr_filter(self, sents: Texts, embds: Tensor, **kwargs) -> str:

    assert "threshold" in kwargs
    assert "terminate" in kwargs

    threshold = kwargs["threshold"]
    terminate = kwargs["terminate"]

    target_vec, mat = embds[0], embds[1:]

    contrib = self.mmr(target_vec, mat)
    sents = sents[1:]

    if contrib is not None:
      pos_idxs = torch.where(contrib > threshold)[0].tolist()
      filtered_sents = [
          sent for idx, sent in enumerate(sents) if idx in pos_idxs
      ]

      if terminate(contrib):
        return " ".join(filtered_sents)
      else:
        return self.mmr_filter(filtered_sents, mat[pos_idxs])

    else:
      return " ".join(sents)

  def mmr(self, t_vec: Tensor, mat: Tensor) -> Optional[Tensor]:

    # NOTE: kaggle version of pytorch gives `RuntimeError`
    # when the matrix is not invertible.

    mat, mat_t = mat.T, mat
    res = mat_t @ mat
    a = torch.linalg.det(res)

    if a > 1e-5:
      contrib = torch.inverse(res) @ mat_t @ t_vec
      return contrib
    else:
      return None

  def cossim_filter(self, texts: Texts, embds: Tensor, **kwargs) -> str:

    assert "top_k" in kwargs

    top_k = kwargs["top_k"]

    target_vec, sents_mat = embds[[0]], embds[1:]
    _, sents = texts[0], texts[1:]

    sim_vec = torch.cosine_similarity(target_vec, sents_mat)
    _, idxs = torch.sort(sim_vec, descending=True)
    k = round(top_k*len(sents))
    idxs = idxs[:k]
    return " ".join([sent for idx, sent in enumerate(sents) if idx in idxs])

  def group_data(self, texts: Texts) -> Tuple[Idxs, Idxs, Texts]:

    _datas: List[Texts] = [*map(self._group_text, texts)]
    text_ids: Idxs = [0, *accumulate(operator.add, map(len, _datas))]
    datas: Texts = [*concat(_datas)]
    batch_sents: List[Texts] = [*map(self.nlp, datas)]

    for i in range(len(batch_sents)):
      batch_sents[i] = [datas[i]] + batch_sents[i]

    sents_ids: Idxs = [0, *accumulate(operator.add, map(len, batch_sents))]
    return text_ids, sents_ids, [*concat(batch_sents)]

  def _group_text(self, text: str) -> Texts:

    def join_sents(sent1: str, sent2: str) -> str:
      if sent1:
        return sent1 + " " + sent2
      else:
        return sent2

    sents = self.nlp(text)
    grp_texts = []
    curr_text = ""
    curr_text_len = 0

    for sent in sents:
      sent_len = len(sent.split())
      if sent_len + curr_text_len < self.max_sent_length:
        curr_text_len += sent_len
        curr_text = join_sents(curr_text, sent)
      else:
        grp_texts.append(curr_text)
        curr_text, curr_text_len = sent, sent_len

    if len(grp_texts) and curr_text_len <= self.tol_sent_len:
      grp_texts[-1] += " " + curr_text
    else:
      grp_texts.append(curr_text)

    return grp_texts

  @staticmethod
  def gather(data: A, idxs: Idxs) -> List[A]:
    acc = []
    for s_idx, e_idx in zip(idxs, idxs[1:]):
      acc.append(data[s_idx:e_idx])
    return acc


Score = float
Doc = Tuple[Score, str]


class SentenceFilling:
  modes = ["greedy"]

  def __init__(self, nlp: Nlp,
               score_fn: Callable[[str], Score],
               max_score: int):
    self.max_score = max_score
    self.nlp = nlp
    self.score_fn = score_fn

  def __call__(self, text: str, datas: List[Doc],
               mode: str = "greedy") -> str:

    assert mode in self.modes

    if mode == "greedy":
      return self.greedy_filling(text, datas)
    else:
      raise NotImplementedError()

  def greedy_filling(self, text: str, datas: List[Doc]) -> str:
    score = self.score_fn(text)
    req_score = self.max_score - score
    datas = sorted(datas, key=lambda data: abs(req_score - data[0]))

    for idx, data in enumerate(datas):

      sel_score, sel_text = data

      if sel_score + score < self.max_score:
        text += " " + sel_text
        return self.greedy_filling(text, datas[idx:])
    return text
