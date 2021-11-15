from ipywidgets import Button,HTML,Layout,Box,Text
from typing import List


class Colors:
  black = "#1F1D36"
  navy = "#3F3351"
  purple = "#864879"
  peach = "#E9A6A6"
  peach2 = "#FDD2BF"
  cold = "#916BBF"
  white = "#F9F9F9"
  pink = "#FFBCBC"
  light_blue = "#88FFF7"
  light_red = "#E98580"
  red = "#DF5E5E"
  light_green = "#CDF0EA"
  light_purple = "#BEAEE2"


class Templates:

  @staticmethod
  def info_template(name: str, tags: List[str]):
    info_style = """
                    <style>
                      ul{
                        list-style: none;
                        margin-bottom: 3%;
                      }
                      li{
                        display: inline;
                        background-color: #1F1D36;
                        color: #F7DBF0;
                        margin-right: 1%;
                        padding: 1%;
                        border: 2px solid;
                        border-radius: 3px;
                        border-color: #916BBF;
                        font-family: Verdana, Geneva, Tahoma, sans-serif;
                      }
                    </style>
                  """
    tag_template = lambda tag_name: f"<li><b>{tag_name}</b></li>"
    tags_html = " ".join([tag_template(tag) for tag in tags])
    info = f"""
              {info_style}
              <p style="background: {Colors.black};">
                <h3 style="color: {Colors.peach2}; text-align-last: center; margin-bottom: 3%;">{name}</h3>
                <ul>
                  <li style="border: none; color: {Colors.light_blue};"><b>Tags: </b></li>
                  {tags_html}
                </ul>
              </p>
              <hr style="border: 1px solid {Colors.light_purple};">
            """
    return HTML(value=info, layout=Layout(flex="3 1 88%"))

  @property
  def loading_widget(self):
    value = """
              <style>
                .loader {
                  border: 6px solid #3F3351;
                  border-top: 6px solid #E9A6A6;
                  border-radius: 50%;
                  width: 40px;
                  height: 40px;
                  animation: spin 2s linear infinite;
                  margin-left: 15%;
                }

                @keyframes spin {
                  0% { transform: rotate(0deg); }
                  100% { transform: rotate(360deg); }
                }
              </style>
              <h3 style="color: #FDD2BF;">searching . . .</h3>
              <div class="loader"></div>
              """
    return HTML(value=value,layout=Layout(flex="0 1 auto",align_self="center"))

  @property
  def logo(self):
    value = """
              <style>
                h1 {
                  background: -webkit-linear-gradient(#FDD2BF, #916BBF);
                  font-size:36px;
                  -webkit-background-clip: text;
                  background-clip: text;
                  -webkit-text-fill-color: transparent;
                  font-family: Verdana;
                }

              </style>

              <h1 class="text">Yuno</h1>
              """
    return HTML(value=value,layout=Layout(flex="0 1 auto",align_self="center"))


  @property
  def search_btn(self):
    btn_style = HTML("""
                      <style>
                        .main-btn {
                                  background-color: #3F3351;
                                  border-radius: 3px;
                                  border: 1px solid #916BBF;

                                  box-sizing: border-box;
                                  color: #FDD2BF;
                                  cursor: pointer;
                                  font-family: Verdana;
                                  font-size: 12px;
                                  outline-color: #916BBF;
                                  margin-top: 5px;
                                }

                        .main-btn:hover,
                        .main-btn:focus {
                          outline: none !important;
                          box-shadow: none !important;
                          background-color: #3F3351;
                          outline-color: #916BBF;
                          color: #FDD2BF;
                        }

                      .main-btn:active {
                        outline: none !important;
                        box-shadow: none !important;
                        background-color: #1F1D36;
                        outline-color: #916BBF;
                        color: #FDD2BF;
                      }
                    </style>""")

    display(btn_style)
    btn = Button(description="search", icon="search", layout=Layout(flex="1 1 15%"))
    btn.add_class("main-btn")
    return btn

  @property
  def info_btn(self):
    btn = Button(description="more info", layout=Layout(flex="1 1 12%"))
    btn.add_class("main-btn")
    return btn

  @property
  def back_btn(self):
    btn_style = HTML("""<style>
                         .back-btn {
                            background-color:#852747;
                            border-radius: 3px;
                            border: 1px solid #916BBF;

                            box-sizing: border-box;
                            color: #CDF0EA;
                            cursor: pointer;
                            font-family: Verdana;
                            font-size: 12px;
                            outline-color: #916BBF;
                          }

                        .back-btn:hover,
                        .back-btn:focus {
                          outline: none !important;
                          box-shadow: none !important;
                        }
                          .back-btn:active {
                            outline: none !important;
                            box-shadow: none !important;
                            background-color: #DF5E5E;
                            outline-color: #916BBF;
                            color: #FDD2BF;
                          }
                        </style>""")
    btn = Button(description="More Info")
    btn.add_class("back-btn")
    return btn

  @property
  def search_bar(self):
    bar_style = HTML("""
                      <style>
                       .searchTerm {
                        border: 3px solid #916BBF;
                        border-radius: 3px;

                      }
                      .searchTerm > input[type="text"] {
                          color: #FDD2BF;
                          font-size: 14px;
                          background: #3F3351;
                      }
                      </style>
                    """)
    display(bar_style)
    search_bar = Text(placeholder="search ...", layout=Layout(flex="3 1 85%"))
    search_bar.add_class("searchTerm")
    return search_bar

