import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pikepdf import Pdf
from pdform import fill_form

pdf = Pdf.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pdfs', 'dd0293.pdf'))
fill_form(pdf, {
    # CASE NUMBER
    "form1[0].page1[0].TextField1[0]":"123456789",
    # DATE OF DISCHARGE (YYYYMMDD) 
    "form1[0].page1[0].DateField2[0]":"20200202",
    # Select for \"ARMY.\"
    "form1[0].page1[0].CheckBox1[0]":False,
    # Select for \"NAVY.\"
    "form1[0].page1[0].CheckBox1[1]":True,
    # Select for \"AIR FORCE.\"
    "form1[0].page1[0].CheckBox1[2]":False,
    # Select for \"COAST GUARD.\"
    "form1[0].page1[0].CheckBox1[3]":False,
    # Select for \"MARINE CORPS.\"
    "form1[0].page1[0].CheckBox1[4]":False,
    # Select for \"SPACE FORCE.\"
    "form1[0].page1[0].CheckBox1[5]":False,
    # Select for \"REGULAR.\"
    "form1[0].page1[0].CheckBox1[6]":False,
    # Select for \"RESERVE.\"
    "form1[0].page1[0].CheckBox1[7]":True,
    # Select for \"GUARD.\"
    "form1[0].page1[0].CheckBox1[8]":False,
    # Enter last name while serving
    "form1[0].page1[0].Subform1[0].TextField1[0]":"Benson",
    # Enter first name while serving
    "form1[0].page1[0].Subform1[0].TextField1[1]":"Ben",
    # Enter current last name
    "form1[0].page1[0].Subform1[1].TextField1[0]":"Benson",
    # Enter current first name
    "form1[0].page1[0].Subform1[1].TextField1[1]":"Ben",
    # 5a. SSN WHILE SERVING \t
    "form1[0].page1[0].TextField1[1]":"123-45-6789",
    # 5b. DoD ID NUMBER (provide, if applicable)
    "form1[0].page1[0].TextField1[2]":"123456789",
    # STREET
    "form1[0].page1[0].TextField1[3]":"123 Example St.",
    # CITY, STATE/APO, COUNTRY/FOREIGN ADDRESS
    "form1[0].page1[0].TextField1[4]":"Anytown, MN",
    # ZIP
    "form1[0].page1[0].TextField1[5]":"12345",
    # EMAIL (Address Required)
    "form1[0].page1[0].TextField1[6]":"ben@example.com",
    # PHONE (Required)
    "form1[0].page1[0].TextField1[7]":"321-654-9870",
    # 7. GRADE/RANK AT DISCHARGE - ARMY - Select from drop-down list.
    "form1[0].page1[0].#subform[2].DropDownList1[0]":" ",
    #7. GRADE/RANK AT DISCHARGE - NAVY- Select from drop-down list.
    "form1[0].page1[0].#subform[2].DropDownList1[1]":"CWO-1",
    #7. GRADE/RANK AT DISCHARGE - AIR FORCE- Select from drop-down list.",
    "form1[0].page1[0].#subform[2].DropDownList1[2]":" ",
    #7. GRADE/RANK AT DISCHARGE - ARMY - Select from drop-down list.",
    "form1[0].page1[0].#subform[2].DropDownList1[3]":" ",
    #7. GRADE/RANK AT DISCHARGE - MARINE CORPS- Select from drop-down list.",
    "form1[0].page1[0].#subform[2].DropDownList1[4]":" ",
    #7. GRADE/RANK AT DISCHARGE - SPACE FORCE- Select from drop-down list.",
    "form1[0].page1[0].#subform[2].DropDownList1[5]":" ",
    #8. HIGHEST GRADE/RANK HELD - ARMY - Select from drop-down list.",
    "form1[0].page1[0].#subform[3].DropDownList1[6]":" ",
    #8. HIGHEST GRADE/RANK HELD - NAVY- Select from drop-down list.",
    "form1[0].page1[0].#subform[3].DropDownList1[7]":"CWO-1",
    #8. HIGHEST GRADE/RANK HELD - AIR FORCE- Select from drop-down list.",
    "form1[0].page1[0].#subform[3].DropDownList1[8]":" ",
    #8. HIGHEST GRADE/RANK HELD - ARMY - Select from drop-down list.",
    "form1[0].page1[0].#subform[3].DropDownList1[9]":" ",
    #8. HIGHEST GRADE/RANK HELD - MARINE CORPS- Select from drop-down list.",
    "form1[0].page1[0].#subform[3].DropDownList1[10]":" ",
    #8. HIGHEST GRADE/RANK HELD - SPACE FORCE- Select from drop-down list.",
    "form1[0].page1[0].#subform[3].DropDownList1[11]":" ",
    # Select for \"UNCHARACTERIZED/ENTRY LEVEL SEPARATION.\"
    "form1[0].page1[0].Subform3[0].CheckBox1[0]":True,
    # Select for \"HONORABLE.\"
    "form1[0].page1[0].Subform3[0].CheckBox1[1]":False,
    # Select for \"BAD CONDUCT DISCHARGE.\"
    "form1[0].page1[0].Subform3[0].CheckBox1[2]":False,
    # Select for \"UNDER HONORABLE CONDITIONS (GENERAL).\"
    "form1[0].page1[0].Subform3[0].CheckBox1[3]":False,
    # Select for \"UNDER OTHER THAN HONORABLE CONDITIONS.\"
    "form1[0].page1[0].Subform3[0].CheckBox1[4]":False,
    # Select for \"CHARACTER OF SERVICE.\"
    "form1[0].page1[0].CheckBox1[9]":True,
    # Select for \"SEPARATION CODE.\"
    "form1[0].page1[0].CheckBox1[10]":True,
    # Select for \"REENTRY CODE.\"
    "form1[0].page1[0].CheckBox1[11]":False,
    # Select for \"NARRATIVE REASON FOR SEPARATION.\"
    "form1[0].page1[0].CheckBox1[12]":True,
    # 11. SEPARATION CODE\n(DD Form 214, box 26)
    "form1[0].page1[0].TextField4[0]":'321',
    # 12. REENTRY CODE\n(DD Form 214, box 27)
    "form1[0].page1[0].TextField4[1]":'654',
    # 13. SEPARATION AUTHORITY\n(DD Form 214, box 25)
    "form1[0].page1[0].TextField4[2]":'Jeff',
    # 14. NARRATIVE REASON (DD Form 214, box 28)
    "form1[0].page1[0].TextField1[8]":'Guacamole',
    # 15. UNIT AND LOCATION AT DISCHARGE
    "form1[0].page1[0].TextField1[9]":'Unit 5, Thither',
    # Select for \"YES.\"
    "form1[0].page1[0].CheckBox1[13]":False,
    # Select for \"NO.\"
    "form1[0].page1[0].CheckBox1[14]":True,
    # 16b. IF YES AND KNOWN, PROVIDE THE CASE NUMBER
    "form1[0].page1[0].TextField1[10]":'None',
    # AND THE DECISION DATE (YYYYMMDD)
    "form1[0].page1[0].DateField4[0]":'20211202',
    # Select for \"CONDUCT INITIAL RECORD REVIEW OF MY DISCHARGE BASED ON MY MILITARY PERSONNEL FILE AND ANY ADDITIONAL DOCUMENTATION SUBMITTED BY ME. I AND/OR (counsel/representative) WILL NOT APPEAR BEFORE THE BOARD.\"
    "form1[0].page1[0].CheckBox1[15]":True,
    # Select for \"I AND/OR (counsel/representative) WISH TO APPEAR AT MY OWN EXPENSE BEFORE THE BOARD.\"
    "form1[0].page1[0].CheckBox1[16]":True,
    # (NOTE: The Naval and Coast Guard Discharge Review Boards do not have traveling boards.)
    "form1[0].page1[0].TextField1[11]":"Things go here I guess?",
    # Select for \"YES.\"
    "form1[0].page1[0].Subform2[0].CheckBox1[0]":False,
    # Select for \"NO.\"
    "form1[0].page1[0].Subform2[0].CheckBox1[1]":False,
    # Select for \"Operation Iraqi Freedom (OIF) (03/19/2003 - 08/31/2010).\"
    "form1[0].page1[0].Subform2[1].CheckBox1[0]":False,
    # Select for \"Operation Freedom Sentinel (OFS) (01/01/2015-Present).\"
    "form1[0].page1[0].Subform2[1].CheckBox1[1]":False,
    # Select for \"Operation Inherent Resolve (OIR) (08/08/2014  - Present).\"
    "form1[0].page1[0].Subform2[1].CheckBox1[2]":False,
    # Select for \"Operation Enduring Freedom (OEF) (09/11/2001  - 12/31/2014).\"
    "form1[0].page1[0].Subform2[1].CheckBox1[3]":False,
    # Select for \"Operation New Dawn (OND) (09/01/2010  - 12/15/2011).\"
    "form1[0].page1[0].Subform2[1].CheckBox1[4]":False,
    # Select for \"OTHER.\"
    "form1[0].page1[0].Subform2[1].CheckBox1[5]":True,
    # Enter specification for \"OTHER\"
    "form1[0].page1[0].Subform2[1].TextField1[0]":"Peacetime",
    # Select for \"PTSD.\"
    "form1[0].page1[0].CheckBox1[17]":False,
    # Select for \"TBI.\"
    "form1[0].page1[0].CheckBox1[18]":False,
    # Select for \"OTHER MENTAL HEALTH.\"
    "form1[0].page1[0].CheckBox1[19]":True,
    # Select for \"SEXUAL ASSAULT/ HARASSMENT.\"
    "form1[0].page1[0].CheckBox1[20]":False,
    # Select for \"DADT.\"
    "form1[0].page1[0].CheckBox1[21]":False,
    # Select for \"TRANSGENDER.\"
    "form1[0].page1[0].CheckBox1[22]":False,
    # Select for \"REPRISAL/ WHISTLEBLOWER.\"
    "form1[0].page1[0].CheckBox1[23]":False,
    # Select for \"INTIMATE PARTNER VIOLENCE/DOMESTIC VIOLENCE.\"
    "form1[0].page1[0].CheckBox1[24]":False,
    # 20. Based on propriety, equity and/or clemency, briefly explain why the Board should grant the requested change. IMPORTANT NOTE:  If the basis of your request involves the effects of one or more physical, medical, mental, and/or behavioral health condition(s) and if available, please attach copies of any VA rating decisions, relevant medical records, and counseling treatment records. Continue on a separate sheet if necessary.
    "form1[0].page2[0].TextField4[0]":"This is the thing and the other thing.\nHey let's put some words in here and make this paragraph so long that it overflows to the next line. That will tell us if the line wrapping is still working okay. It's important to wrap lines or you won't be able to see what's at the end. For example, here's a smiley face you would have totally missed out on:  :-)",
    # 21a. IN SUPPORT OF THIS CLAIM, THE FOLLOWING DOCUMENTARY EVIDENCE IS ATTACHED (LIST DOCUMENTS): Example evidence / records: Separation packet, medical documents (e.g. diagnosis, VA rating), post-service documents (e.g. diplomas, professional certificates, character references), and/or investigations. (Do NOT submit irreplaceable original documents. They will NOT be returned.) - item 1.
    "form1[0].page2[0].#subform[0].TextField1[0]":"Item 1",
    # 21a. IN SUPPORT OF THIS CLAIM, THE FOLLOWING DOCUMENTARY EVIDENCE IS ATTACHED (LIST DOCUMENTS): Example evidence / records: Separation packet, medical documents (e.g. diagnosis, VA rating), post-service documents (e.g. diplomas, professional certificates, character references), and/or investigations. (Do NOT submit irreplaceable original documents. They will NOT be returned.) - item 2.
    "form1[0].page2[0].#subform[0].TextField1[1]":"Item 2",
    # 21a. IN SUPPORT OF THIS CLAIM, THE FOLLOWING DOCUMENTARY EVIDENCE IS ATTACHED (LIST DOCUMENTS): Example evidence / records: Separation packet, medical documents (e.g. diagnosis, VA rating), post-service documents (e.g. diplomas, professional certificates, character references), and/or investigations. (Do NOT submit irreplaceable original documents. They will NOT be returned.) - item 3.
    "form1[0].page2[0].#subform[0].TextField1[2]":"Item 3",
    # 21b. IN SUPPORT OF THIS CLAIM, THE FOLLOWING DOCUMENTARY EVIDENCE IS ATTACHED (LIST DOCUMENTS): Example evidence / records: Separation packet, medical documents (e.g. diagnosis, VA rating), post-service documents (e.g. diplomas, professional certificates, character references), and/or investigations. (Do NOT submit irreplaceable original documents. They will NOT be returned.) - item 1.
    "form1[0].page2[0].#subform[1].TextField1[3]":"Do we really need all these?",
    # 21b. IN SUPPORT OF THIS CLAIM, THE FOLLOWING DOCUMENTARY EVIDENCE IS ATTACHED (LIST DOCUMENTS): Example evidence / records: Separation packet, medical documents (e.g. diagnosis, VA rating), post-service documents (e.g. diplomas, professional certificates, character references), and/or investigations. (Do NOT submit irreplaceable original documents. They will NOT be returned.) - item 2.
    "form1[0].page2[0].#subform[1].TextField1[4]":"Last one, the rest can be blank",
    # 21b. IN SUPPORT OF THIS CLAIM, THE FOLLOWING DOCUMENTARY EVIDENCE IS ATTACHED (LIST DOCUMENTS): Example evidence / records: Separation packet, medical documents (e.g. diagnosis, VA rating), post-service documents (e.g. diplomas, professional certificates, character references), and/or investigations. (Do NOT submit irreplaceable original documents. They will NOT be returned.) - item 3.
    "form1[0].page2[0].#subform[1].TextField1[5]":"",
    # 21c. IN SUPPORT OF THIS CLAIM, THE FOLLOWING DOCUMENTARY EVIDENCE IS ATTACHED (LIST DOCUMENTS): Example evidence / records: Separation packet, medical documents (e.g. diagnosis, VA rating), post-service documents (e.g. diplomas, professional certificates, character references), and/or investigations. (Do NOT submit irreplaceable original documents. They will NOT be returned.) - item 1.
    "form1[0].page2[0].#subform[2].TextField1[6]":"",
    # 21c. IN SUPPORT OF THIS CLAIM, THE FOLLOWING DOCUMENTARY EVIDENCE IS ATTACHED (LIST DOCUMENTS): Example evidence / records: Separation packet, medical documents (e.g. diagnosis, VA rating), post-service documents (e.g. diplomas, professional certificates, character references), and/or investigations. (Do NOT submit irreplaceable original documents. They will NOT be returned.) - item 2.
    "form1[0].page2[0].#subform[2].TextField1[7]":"",
    # 21c. IN SUPPORT OF THIS CLAIM, THE FOLLOWING DOCUMENTARY EVIDENCE IS ATTACHED (LIST DOCUMENTS): Example evidence / records: Separation packet, medical documents (e.g. diagnosis, VA rating), post-service documents (e.g. diplomas, professional certificates, character references), and/or investigations. (Do NOT submit irreplaceable original documents. They will NOT be returned.) - item 3.
    "form1[0].page2[0].#subform[2].TextField1[8]":"",
    # Select for \"REPRESENTATIVE.\"
    "form1[0].page2[0].CheckBox1[0]":True,
    # Select for \"ATTORNEY.\"
    "form1[0].page2[0].CheckBox1[1]":True,
    # Enter representative or counsel's last name.
    "form1[0].page2[0].Subform1[0].TextField1[0]":"Dum",
    # Enter representative or counsel's first name.
    "form1[0].page2[0].Subform1[0].TextField1[1]":"Dum",
    # STREET
    "form1[0].page2[0].TextField1[9]":"789 Any Way",
    # CITY, STATE/APO, COUNTRY/FOREIGN ADDRESS
    "form1[0].page2[0].TextField1[10]":"Metropolis, NY",
    # ZIP
    "form1[0].page2[0].TextField1[11]":"98765",
    # EMAIL (Required)
    "form1[0].page2[0].TextField1[12]":"dumdum@example.org",
    # PHONE (Required)
    "form1[0].page2[0].TextField1[13]":"987-654-3210",
    # ENTER NAME
    "form1[0].page2[0].TextField6[0]":"Benita Benson",
    # Select for \"SPOUSE.\"
    "form1[0].page2[0].CheckBox1[2]":True,
    # Select for \"WIDOW.\"
    "form1[0].page2[0].CheckBox1[3]":False,
    # Select for \"WIDOWER.\"
    "form1[0].page2[0].CheckBox1[4]":False,
    # Select for \"NEXT OF KIN.\"
    "form1[0].page2[0].CheckBox1[5]":False,
    # Select for \"LEGAL REPRESENTATIVE.\"
    "form1[0].page2[0].CheckBox1[6]":False,
    # Select for \"OTHER.\"
    "form1[0].page2[0].CheckBox1[7]":False,
    # Enter specification for \"OTHER\"
    "form1[0].page2[0].TextField1[14]":"Nope",
    # Select for \"YES.\"
    "form1[0].page2[0].CheckBox1[8]":True,
    # Select for \"NO.\"
    "form1[0].page2[0].CheckBox1[9]":False,
    # 25b. SIGNATURE (Required)
    "form1[0].page2[0].SignatureField1[0]":os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', 'sigtest.jpg'),
    # 25c. DATE SIGNED (YYYYMMDD)
    "form1[0].page2[0].DateField3[0]":"20230220",
})
pdf.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output', 'fill_form_dd0293.pdf'))