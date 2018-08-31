import PyPDF2

def getPDFContent(path):

    content = ""

    pdf = PyPDF2.PdfFileReader(file(path, "rb"))

    for i in range(0, pdf.getNumPages()):
        f=open("P://Study/Project_870/PDFs/Huxley1.txt",'a')
        content= pdf.getPage(i).extractText() + "\n"
        import string
        c=content.split()
        for a in c:
            f.write(" ")
            f.write(a)
        f.write('\n')
        f.close()

    return content

print (getPDFContent("P://Study/Project_870/PDFs/Huxley1.pdf"))