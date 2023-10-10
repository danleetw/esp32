!pip install PyPDF2 requests
!pip install genanki

######################################################################
# 本程式提供有興趣報考業餘無線電人員準備考試用工具
# 非營利用途，資料來源來自"國家通訊傳播委員會公開PDF
# https://nccmember.ncc.gov.tw/exam/application/exam/examc07new.aspx
# 轉換結果亦請勿移作營利用途
# 本程式係由ChatGPT協助完成
# 原理是由NCC取得PDF內容
# 將取得內容用正規化表示式取得題目跟內容
# 然後用GenAnki Library轉換成AKPG卡片檔案，讓使用者下載
# 在一天前我完全不知道可以透過Colab直接轉換成APKG檔案並直接下載
# 科技實在太神奇了
# 影片在此
# https://www.youtube.com/watch?v=0Xz2v4eF9sU
######################################################################
import re
import requests
from PyPDF2 import PdfReader
from io import BytesIO
from google.colab import files
from openpyxl import Workbook
import csv
import genanki

def fullwidth_to_halfwidth(s):
    """Convert full-width characters to half-width characters."""
    return ''.join([chr(ord(c) - 0xFEE0) if 0xFF01 <= ord(c) <= 0xFF5E else c for c in s])

# 下載PDF


url3 = "https://www.ncc.gov.tw/chinese/files/21080/649_45743_210806_1.pdf"
url2 = "https://www.ncc.gov.tw/chinese/files/service_file/0_1084_201014_2.pdf"
url1 = "https://www.ncc.gov.tw/chinese/files/service_file/0_1084_201014_1.pdf"
lib_strs=[r'無線電規章 與相關法規題庫',r'無線電通訊方法題庫',r'無線電系統原理 題庫',r'用歐姆表測量電路中的電阻']
lib_strs=[r'無線電規章 與相關法規題庫',r'無線電通訊方法題庫',r'無線電系統原理 題庫',r'無線電相關安全防護 題庫',r'電磁相容性技術 題庫',r'射頻干擾的預防與排除 題庫',r'請準備最近']

filename = 'output.xlsx'
filename1 = 'output.csv'

def getLib(url,filename):
  ret_list=list()

  response = requests.get(url)
  # 確認請求成功
  if response.status_code == 200:
      # 使用BytesIO將內容轉換為二進制流
      pdf_file = BytesIO(response.content)

      # 使用PyPDF2的PdfReader從二進制流讀取PDF內容
      reader = PdfReader(pdf_file)
      pdf_text = ""
      all_text=""

      # 讀入所有文字
      for page in reader.pages:
          all_text += page.extract_text()  # 注意這裡改為 extract_text

      pattern = re.compile(r'分配頻段內發射方式之頻率範圍應'+r'(.*?)'+r'吋光面照片', re.DOTALL)
      match = pattern.search(all_text)
      if match:
        all_text = match.group(1).strip()
      else:
        print("抓取錯誤!!!")

      # 開啟Excel檔案並寫入
      wb = Workbook()
      ws = wb.active


      for seg_index,seg_str in enumerate(lib_strs[:-1]):
        print(seg_index,seg_str,lib_strs[seg_index+1])
        pattern = re.compile(seg_str+r'(.*?)'+lib_strs[seg_index+1], re.DOTALL)
        match = pattern.search(all_text)
        if match:
          extracted_content = match.group(1).strip()
          #print(extracted_content)
          text=extracted_content
          print("Match!")
          #print(text)
        else:
          print("Not Match!")
          #print(text[4000:5000])
          #print(text.find(r'無線電規章'))


        # 定義正則表達式模式
        # 重新設定 pattern_str 來捕捉題目與其四個答案
        #pattern_str = r'\(\s*(\d)\s*\)\s*(\d{1,3}\..*?)(\(\d\)\s*.*?\(\d\)\s*.*?\(\d\)\s*.*?\(\d\)\s*.*?)\s*(?=\(\s*\d\s*\)|$)'
        #pattern_str = r'\s*\(\s*(\d)\s*\)\s*(\d{1,3}\..*?)(\(\d\)\s*.*?\(\d\)\s*.*?\(\d\)\s*.*?\(\d\)\s*.*?)\s*(?=\(\s*\d\s*\)|$)'
        #pattern_str = r'\(\s*(\d)\s*\)\s*((?:\d\s*)+\..*?)(\(\d\)\s*.*?\(\d\)\s*.*?\(\d\)\s*.*?\(\d\)\s*.*?)\s*(?=\(\s*\d\s*\)|$)'
        pattern_str = r'\(\s*(\d)\s*\)\s*((?:\d\s*)+)\.\s*(.*?)(\(\d\)\s*.*?\(\d\)\s*.*?\(\d\)\s*.*?\(\d\)\s*.*?)\s*(?=\(\s*\d\s*\)|$)'



        answer_pattern_str = r'\((\d)\)\s*(.*?)\s*(?=\(\d\)|$)'

        pattern = re.compile(pattern_str, re.DOTALL)
        answer_pattern = re.compile(answer_pattern_str, re.DOTALL)

        text=fullwidth_to_halfwidth(text)
        questions = pattern.findall(text)


        qcnt=0
        for q in questions:
            qcnt+=1
            #print(q)
            #aaa
            correct_answer, question_no,question_text, all_answers = q

            question_no=("  "+question_no.replace(" ",""))[-3:]
            w_str=""+question_no+"."+question_text.strip()+"<BR>"
            c_ans=""

            answers = answer_pattern.findall(all_answers)
            for ans_num, ans_text in answers:
                if ans_num==correct_answer:
                  c_ans=ans_text

                w_str+=ans_num+" "+ans_text.strip() + "<BR>"
            w_str=w_str

            #if qcnt>=3:
            ws.append([f"{w_str}", correct_answer+" "+c_ans,seg_str.replace(" ","")])
            ret_list.append( {'q':w_str , 'a':correct_answer +" "+c_ans , 't':[seg_str.replace(" ",""),] } )
    # Save workbook to a file

  wb.save(filename)


  # 使用csv模組將ws物件輸出成CSV檔案
  with open(filename1, "w", newline="", encoding="utf-8") as f:
      writer = csv.writer(f)
      for row in ws.iter_rows(values_only=True):
          writer.writerow(row)
  # 下載XLSX檔案
  #files.download(filename)
  # 下載CSV檔案
  #files.download(filename)
  return ret_list


def GenAnkiCard(apkg_name,qa_list,apkg_filename):
  import genanki
  import random

  # 定義模型（Model）
  model = genanki.Model(
    model_id=random.randrange(1 << 30, (1 << 31) - 1),  # 隨機生成 Model ID
    name=apkg_name,
    fields=[
      {'name': 'Question'},
      {'name': 'Answer'},
    ],
    templates=[
      {
        'name': 'Card 1',
        'qfmt': '{{Question}}',
        'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}',
      },
    ])

  # 定義牌組（Deck），並生成隨機的 Deck ID
  deck = genanki.Deck(
    deck_id=random.randrange(1 << 30, (1 << 31) - 1),
    name=apkg_name)


  # 將問題和答案加到牌組中，並添加標籤
  for qa in qa_list:
      note = genanki.Note(
          model=model,
          fields=[qa["q"], qa["a"]],
          tags=qa.get("t", [])  # 如果 qa 字典中有 "t" 鍵，則使用其值作為標籤；否則使用空列表。
      )
      deck.add_note(note)

  # 建立 .apkg 檔案
  genanki.Package(deck).write_to_file(apkg_filename)
  # 下載apkg 檔案
  files.download(apkg_filename)




akp_list=getLib(url1,"NCC業餘無線電一等題庫.csv")
GenAnkiCard("NCC業餘無線電一等題庫",akp_list,"NCC業餘無線電一等題庫.apkg")
akp_list=getLib(url2,"NCC業餘無線電二等題庫.csv")
GenAnkiCard("NCC業餘無線電二等題庫",akp_list,"NCC業餘無線電二等題庫.apkg")
akp_list=getLib(url3,"NCC業餘無線電三等題庫.csv")
GenAnkiCard("NCC業餘無線電三等題庫",akp_list,"NCC業餘無線電三等題庫.apkg")

#print(akp_list)
#getLib(url2,"NCC業餘無線電二等題庫.csv")
#getLib(url3,"NCC業餘無線電三等題庫.csv")

print("Done!")

