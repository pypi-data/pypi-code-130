import scipdf
import time
import os

def extract_text(paper):
    # Get paper
    path = os.path.dirname(os.path.abspath(__file__))

    os.system('nohup /home/maamari/Documents/Github/artk/artk/gradle/gradlew -p /home/maamari/Documents/Github/artk/artk/gradle/ run >Output.log 2>&1 &'.format(path,path))    
    time.sleep(15)

    if len(paper):
        article_dict = scipdf.parse_pdf_to_dict(paper, as_list=True)
    else:
        article_dict = scipdf.parse_pdf_to_dict('https://arxiv.org/pdf/1811.05477.pdf', as_list=True)
    os.system('pkill java')

    return article_dict

if __name__=='__main__':
    extract_text("https://arxiv.org/pdf/1811.05477.pdf")
