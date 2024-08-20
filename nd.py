def gerar_nota(name,base_final,i,day_date, mounth, mounth_date, year_date):     
        
        from datetime import date, datetime
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors
        from reportlab.platypus import Table
        from reportlab.lib.units import inch
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont

        pdfmetrics.registerFont(TTFont('Calibri', 'static/fonts/calibri.ttf'))
        pdfmetrics.registerFont(TTFont('CalibriBold', 'static/fonts/calibrib.ttf'))
        pdfmetrics.registerFont(TTFont('CalibriIt', 'static/fonts/calibrii.ttf'))
        pdfmetrics.registerFont(TTFont('Calibriz', 'static/fonts/calibriz.ttf'))

                
        pdf = canvas.Canvas(name, pagesize=(600,900))

        def init_page(pdf):
                    
                    pdf.setFillColorRGB(0/256,0/256,0/256)
                    pdf.setStrokeColorRGB(0/256,0/256,0/256)
                    pdf.setFont("CalibriBold", 12) #choose your font type and font size
                    pdf.drawString(230,850,"Casa dos Ventos Comercializadora de Energia S.A.")
                    pdf.drawImage("static/Logos/Simbolo_BRANCO.jpg",20,835,height=45,width=160)
                    pdf.setFillColorRGB(191/256,191/256,191/256)
                    pdf.rect(21, 800, 559 , 20, fill=1,stroke=0)
                    pdf.rect(21, 490, 559 , 20, fill=1,stroke=0)
                    pdf.rect(21,305,559,20,fill=1,stroke=0)
                    pdf.setFillColorRGB(0/256,0/256,0/256)
                    pdf.drawString(240,805,"Nota de Débito - 001")
                    pdf.rect(20, 685, 560 , 135)
                    pdf.rect(20, 530, 560 , 135)
                    pdf.rect(20, 350, 560 , 160)
                    pdf.drawString(250,495,"Dados da ND")
                    pdf.drawString(245,310,"Dados Bancários")
                    pdf.line(190,489,190,350)
                    pdf.line(20,489,580,489)
                    pdf.line(20,410,580,410)
                    pdf.line(20,390,580,390)
                    pdf.line(20,370,580,370)
                    pdf.rect(20,225,560,100)
                    pdf.line(190,304,190,225)
                    pdf.line(20,304,580,304)
                    pdf.line(20,285,580,285)
                    pdf.line(20,265,580,265)
                    pdf.line(20,245,580,245)
                    pdf.setFont("Calibri", 12)
                    pdf.setFillColorRGB(0/256,0/256,0/256)
                    pdf.setStrokeColorRGB(0/256,0/256,0/256)
                    pdf.rect(1,205,598,694)
                    pdf.drawString(200,180,"Fortaleza - CE, " + day_date + " de " + mounth[mounth_date-1] + " de " + year_date)
                    pdf.line(20,160,560,160)
                    pdf.drawString(180,140,"Casa dos Ventos Comercializadora de Energia S.A.")
                    
                    return pdf   
                
        def Q1(pdf):
            pdf.setFont("Calibri", 12)
            pdf.setFillColorRGB(0/256,0/256,0/256)
            pdf.setStrokeColorRGB(0/256,0/256,0/256)
            pdf.drawString(21,787," CNPJ")
            pdf.drawString(190,787,"33.933.760/0001-00")
            pdf.drawString(21,772," Endereço")
            pdf.drawString(190,772,"AVENIDA DESEMBARGADOR MOREIRA, 1300 - SALA 902 T-NORTE")
            pdf.drawString(21,756," Bairro")
            pdf.drawString(190,756,"ALDEOTA")
            pdf.drawString(21,740," Cidade")
            pdf.drawString(190,740,"FORTALEZA")
            pdf.drawString(21,724," UF")
            pdf.drawString(190,724,"CEARÁ")
            pdf.drawString(21,708," CEP")
            pdf.drawString(190,708,"60.170-002")
            pdf.drawString(21,692," Telefone")
            pdf.drawString(190,692,"(85) 3034.9774")
                    
            
            return pdf

        def Q2(pdf,base_final, i):
            pdf.setFont("Calibri", 12)
            pdf.setFillColorRGB(0/256,0/256,0/256)
            pdf.setStrokeColorRGB(0/256,0/256,0/256)
            pdf.drawString(21,653," Razão social")
            pdf.setFont("CalibriBold", 12)
            pdf.drawString(190,653,str(base_final.iloc[i]['Nome']))
            pdf.setFont("Calibri", 12)
            pdf.drawString(21,638," CNPJ")
            pdf.drawString(190,638, str(base_final.iloc[i]['counterpartyCNPJ']))
            pdf.drawString(21,622," Endereço")
            pdf.drawString(190,622,str(base_final.iloc[i]['Endereço']))
            pdf.drawString(21,606," Bairro")
            pdf.drawString(190,606,str(base_final.iloc[i]['Bairro']))
            pdf.drawString(21,590," Cidade")
            pdf.drawString(190,590,str(base_final.iloc[i]['Cidade']))
            pdf.drawString(21,574," UF")
            pdf.drawString(190,574,str(base_final.iloc[i]['UF']))
            pdf.drawString(21,558," CEP")
            pdf.drawString(190,558,str(base_final.iloc[i]['CEP']))
            pdf.drawString(21,542," Telefone")
            pdf.drawString(190,542,str(base_final.iloc[i]['Telefone']))
                    
            
            return pdf

        def Q3(pdf,base_final, i):
            
            pdf.drawString(21,475," Descrição do Objeto")
            pdf.setFont("Calibri", 11)
            pdf.drawString(190,475," Nota de Débito correspondente ao valor referente à ressarcimento a ser")
            pdf.drawString(190,460," efetuado a Casa dos Ventos Comercializadora de Energia S.A. referente à entrega ")
            pdf.drawString(190,445," inferior do desconto contratado, conforme demonstrado no cálculo em anexo.  ")
            pdf.drawString(190,430," CNPJ para pagamento 33.933.760/0001-00")
            pdf.setFont("Calibri", 12)
            pdf.drawString(21,395," Competência")
            pdf.drawString(190,395," " +str(base_final.iloc[i]['Mês']))
            pdf.drawString(21,375," Valor")
            width = pdf._pagesize[0]
            padding = 25
            pdf.drawRightString(width - padding, 375,"R$ " + str(base_final.iloc[i]['sum']))
            pdf.drawString(21,355," Data de Vencimento")
            pdf.drawString(190,355," " +str(base_final.iloc[i]['vencimento']))
            
            return pdf

        def Q4(pdf):
            pdf.drawString(21,290," Cnpj")
            pdf.drawString(190,290," 33.933.760/0001-00 - Matriz")
            pdf.drawString(21,270," Banco")
            pdf.drawString(190,270," SANTANDER - 033")
            pdf.drawString(21,250," Agência")
            pdf.drawString(190,250," 2271")
            pdf.drawString(21,230," Conta")
            pdf.drawString(190,230," 13088857-6")
            return pdf


        pdf = init_page(pdf)    
        pdf = Q1(pdf)  
        pdf = Q2(pdf,base_final,i)  
        pdf = Q3(pdf,base_final,i)  
        pdf = Q4(pdf) 
        pdf.save()