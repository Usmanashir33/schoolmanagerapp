from .models import TEMPLATE_TYPE
CUSTOM_TEMPLATE_LIST = [temp[0] for temp in TEMPLATE_TYPE]

# #--------------------------------------------------------------------------------
# #                                   SAMPLE TEMPLATES
# #--------------------------------------------------------------------------------
ReportConfigPremium = {
    'stampX': 52, 
    'stampY': 62, 
    'showStamp': True, 
    'stampRotation': 360,
    'stampStyle': {
        'width': '110px', 
        'height': '110px', 
        'opacity': 25, 
        'borderRadius': '50%'
    },
    'signatures': ['Registrar', 'Principal'],
    'signatureStyle': {
        'color': '#0f172a', 
        'border': '', 
        'margin': '56px 0 0 0', 
        'padding': '', 
        'fontSize': '0.95em', 
        'boxShadow': '', 
        'fontStyle': 'normal', 
        'textAlign': 'center', 
        'fontFamily': 'inherit', 
        'fontWeight': '500', 
        'borderRadius': '', 
        'backgroundColor': ''
    },
    'tableStyle': 'bordered',
    'borderColor': '#e2e8f0', 
    'tableCellPadding': '10px 14px', 
    'tableHeaderStyle': {
        'color': '#ffffff', 
        'border': '', 
        'margin': '', 
        'padding': '', 
        'fontSize': '1.1em', 
        'boxShadow': '', 
        'fontStyle': 'normal', 
        'textAlign': 'left', 
        'fontFamily': 'inherit', 
        'fontWeight': '600', 
        'borderRadius': '', 
        'backgroundColor': '#0a1d37' # Rich Deep Luxury Navy
    }, 
    'tableBodyStyle': {
        'color': '#334155', 
        'border': '', 
        'margin': '', 
        'padding': '', 
        'fontSize': '1em', 
        'boxShadow': '', 
        'fontStyle': 'normal', 
        'textAlign': 'left', 
        'fontFamily': 'inherit', 
        'fontWeight': 'normal', 
        'borderRadius': '', 
        'backgroundColor': ''
    }, 
    'titleStyle': {
        'color': '#1e293b', 
        'border': '1px solid #e2e8f0', 
        'margin': '0 auto 24px auto', 
        'padding': '8px 32px', 
        'fontSize': '1.3em', 
        'boxShadow': '0 1px 2px 0 rgba(0, 0, 0, 0.05)', 
        'fontStyle': 'normal', 
        'textAlign': 'center', 
        'fontFamily': 'inherit', 
        'fontWeight': '600', 
        'borderRadius': '6px', 
        'backgroundColor': '#f8fafc' # Clean Minimalist Title Bar instead of giant solid bubble
    }, 
    'headerStyle': 'standard', 
    'headerStyleObj': {
        'color': '#0f172a', 
        'border': '0 0 1px 0 solid #e2e8f0', 
        'margin': '0 0 32px 0', 
        'padding': '0 0 20px 0', 
        'fontSize': '1.2em', 
        'boxShadow': '', 
        'fontStyle': 'normal', 
        'textAlign': 'center', 
        'fontFamily': 'inherit', 
        'fontWeight': 'normal', 
        'borderRadius': '', 
        'backgroundColor': ''
    }, 
    'schoolNameStyle': {
        'color': '#0a1d37', 
        'border': '', 
        'margin': '0 0 4px 0', 
        'padding': '', 
        'fontSize': '1.8em', 
        'boxShadow': '', 
        'fontStyle': 'normal', 
        'textAlign': 'center', 
        'fontFamily': 'inherit', 
        'fontWeight': '800', 
        'borderRadius': '', 
        'backgroundColor': 'transparent'
    }, 
    'schoolNameSecondaryStyle': {
        'color': '#b45309', # Matte Amber Gold Accent
        'border': '', 
        'margin': '', 
        'padding': '', 
        'fontSize': '14px', 
        'boxShadow': '', 
        'fontStyle': 'normal', 
        'textAlign': 'center', 
        'fontFamily': 'inherit', 
        'fontWeight': '600', 
        'borderRadius': '', 
        'backgroundColor': 'transparent'
    },
    'logoPosition': 'left', 
    'logoStyle': {
        'width': '90px', 
        'height': '90px', 
        'opacity': 100, 
        'borderRadius': '12px' # Modern soft corner radius
    },
    'orientation': 'portrait', 
    'showBarcode': True, 
    'barcodeStyle': {
        'width': '100px', 
        'height': '100px'
    }, 
    'showRemarks': True, 
    'remarksStyle': {
        'color': '#334155', 
        'border': '1px solid #e2e8f0', 
        'margin': '24px 0 0 0', 
        'padding': '20px', 
        'fontSize': '0.95em', 
        'boxShadow': '0 1px 3px 0 rgba(0, 0, 0, 0.02)', 
        'fontStyle': 'normal', 
        'textAlign': 'left', 
        'fontFamily': 'inherit', 
        'fontWeight': 'normal', 
        'borderRadius': '8px', 
        'backgroundColor': '#f8fafc'
    }, 
    'skillsStyle': {
        'color': '#0f172a', 
        'fontSize': '1.1em', 
        'fontStyle': 'normal', 
        'textAlign': 'left', 
        'fontFamily': 'inherit', 
        'fontWeight': '600'
    }, 
    'showTextArea': False, 
    'textAreaContent': 'Enter your custom text here...', 
    'textAreaStyle': {
        'color': '#334155', 
        'border': '1px solid #e2e8f0', 
        'margin': '0 0 24px 0', 
        'padding': '16px', 
        'fontSize': '1em', 
        'boxShadow': '', 
        'fontStyle': 'normal', 
        'minHeight': '150px', 
        'textAlign': 'left', 
        'fontFamily': 'inherit', 
        'fontWeight': 'normal', 
        'borderRadius': '6px', 
        'backgroundColor': '#ffffff'
    }, 
    'templateType': 'Report', 
    'documentTitle': 'Official Academic Record', # Enhanced terminology
    'showSeparator': False, 
    'separatorStyle': {
        'color': '#cbd5e1', 
        'border': '1px solid #cbd5e1', 
        'margin': '16px 0', 
        'fontSize': '14px', 
        'fontStyle': 'normal', 
        'textAlign': 'left', 
        'fontFamily': 'inherit', 
        'fontWeight': 'normal'
    }, 
    'watermarkType': 'icon', 
    'watermarkText': 'OFFICIAL', 
    'watermarkImage': '', 
    'watermarkSize': 140, 
    'watermarkOpacity': 4, # Subtler blend so it doesn't distract readability
    'watermarkRotation': -45, 
    'containerStyle': {
        'color': '#1e293b', 
        'border': '1px solid #e2e8f0', 
        'margin': '0 auto', 
        'padding': '50px 45px', # Generous whitespace formatting
        'fontSize': '14px', 
        'boxShadow': '0 10px 25px -5px rgba(0, 0, 0, 0.05)', # Ultra smooth modern shadow
        'fontStyle': 'normal', 
        'textAlign': 'left', 
        'fontFamily': 'inherit', 
        'fontWeight': 'normal', 
        'borderRadius': '12px', 
        'backgroundColor': '#ffffff' # Absolute clean crisp white backdrop
    }, 
    'footerStyleObj': {
        'color': '#64748b', 
        'border': '1px solid #e2e8f0', 
        'margin': 'auto 0 0 0', 
        'padding': '16px 0 0 0', 
        'fontSize': '0.85em', 
        'boxShadow': '', 
        'fontStyle': 'normal', 
        'textAlign': 'center', 
        'fontFamily': 'inherit', 
        'fontWeight': 'normal', 
        'borderRadius': '', 
        'backgroundColor': 'transparent'
    }, 
    'visibleSections': {
        'stamp': True, 
        'table': True, 
        'title': True, 
        'footer': True, 
        'header': True, 
        'remarks': True, 
        'signatures': True, 
        'studentInfo': True
    }, 
    'globalFontFamily': 'Inter, system-ui, sans-serif', # Crisp high-end layout fonts
    'showStudentPhoto': True, # Enabled for premium presentation layout
    'studentPhotoStyle': {
        'width': '110px', 
        'height': '110px', 
        'opacity': 100, 
        'borderRadius': '8px',
        'border': '2px solid #e2e8f0'
    },
    'studentInfoFields': ['name', 'admissionNo', 'gender', 'positionInClass', 'term', 'classRoom'], 
    'studentInfoStyle': {
        'color': '#0f172a', 
        'border': '1px solid #e2e8f0', 
        'margin': '0 0 32px 0', 
        'padding': '20px', 
        'fontSize': '1em', 
        'boxShadow': '0 1px 2px 0 rgba(0, 0, 0, 0.02)', 
        'fontStyle': 'normal', 
        'textAlign': 'left', 
        'fontFamily': 'inherit', 
        'fontWeight': 'normal', 
        'borderRadius': '8px', 
        'backgroundColor': '#f8fafc'
    }, 
    'primaryColor': '#0a1d37'
}

# report_configs.py

ReportConfigStandard = {
    'stampX': 52, 
    'stampY': 62, 
    'showStamp': True, 
    'stampRotation': 360,
    'stampStyle': {'width': '100px', 'height': '100px', 'opacity': 22, 'borderRadius': '50%'},
    'signatures': ['Registrar', 'Principal'],
    'signatureStyle': {'color': 'inherit', 'border': '', 'margin': '48px 0 0 0', 'padding': '', 'fontSize': 'inherit', 'boxShadow': '', 'fontStyle': 'normal', 'textAlign': 'center', 'fontFamily': 'inherit', 'fontWeight': 'normal', 'borderRadius': '', 'backgroundColor': ''},
    'tableStyle': 'bordered',
    'borderColor': '#cccccc', 
    'tableCellPadding': '8px', 
    'tableHeaderStyle': {'color': '#032863', 'border': '', 'margin': '', 'padding': '', 'fontSize': '1.5em', 'boxShadow': '', 'fontStyle': 'normal', 'textAlign': 'left', 'fontFamily': 'inherit', 'fontWeight': 'bold', 'borderRadius': '', 'backgroundColor': ''}, 
    'tableBodyStyle': {'color': 'inherit', 'border': '', 'margin': '', 'padding': '', 'fontSize': '1.5em', 'boxShadow': '', 'fontStyle': 'normal', 'textAlign': 'left', 'fontFamily': "'Times New Roman'", 'fontWeight': 'normal', 'borderRadius': '', 'backgroundColor': ''}, 
    'titleStyle': {'color': '#ffffff', 'border': '', 'margin': '-10px 10vw', 'padding': '4px 24px', 'fontSize': '1.2em', 'boxShadow': '', 'fontStyle': 'normal', 'textAlign': 'center', 'fontFamily': 'inherit', 'fontWeight': 'bold', 'borderRadius': '9999px', 'backgroundColor': '#072440'}, 
    'headerStyle': 'standard', 
    'headerStyleObj': {'color': 'inherit', 'border': '0 0 2px 0 solid #003366', 'margin': '0 0 24px 0', 'padding': '0 0 16px 0', 'fontSize': '1.2em', 'boxShadow': '', 'fontStyle': 'normal', 'textAlign': 'center', 'fontFamily': 'inherit', 'fontWeight': 'normal', 'borderRadius': '', 'backgroundColor': ''}, 
    'schoolNameStyle': {'color': '#061f37', 'border': '', 'margin': '', 'padding': '', 'fontSize': '1.5em', 'boxShadow': '', 'fontStyle': 'normal', 'textAlign': 'center', 'fontFamily': 'inherit', 'fontWeight': 'bold', 'borderRadius': '', 'backgroundColor': '#edf5ff'}, 
    'schoolNameSecondaryStyle': {'color': '#003366', 'border': '', 'margin': '', 'padding': '', 'fontSize': '18px', 'boxShadow': '', 'fontStyle': 'normal', 'textAlign': 'center', 'fontFamily': 'inherit', 'fontWeight': 'bold', 'borderRadius': '', 'backgroundColor': ''},
    'logoPosition': 'left', 
    'logoStyle': {'width': '100px', 'height': '100px', 'opacity': 100, 'borderRadius': '5%'},
    'orientation': 'portrait', 
    'showBarcode': True, 
    'barcodeStyle': {'width': '120PX', 'height': '120PX'}, 
    'showRemarks': True, 
    'remarksStyle': {'color': 'inherit', 'border': '1px solid #d1d5db', 'margin': '0 0 16px 0', 'padding': '16px', 'fontSize': 'inherit', 'boxShadow': '', 'fontStyle': 'normal', 'textAlign': 'left', 'fontFamily': 'inherit', 'fontWeight': 'normal', 'borderRadius': '4px', 'backgroundColor': '#edf5f8'}, 
    'skillsStyle': {'color': '#333333', 'fontSize': '1.5em', 'fontStyle': 'normal', 'textAlign': 'center', 'fontFamily': 'Arial', 'fontWeight': 'normal'}, 
    'showTextArea': False, 
    'textAreaContent': 'Enter your custom text here...', 
    'textAreaStyle': {'color': 'inherit', 'border': '', 'margin': '0 0 24px 0', 'padding': '16px', 'fontSize': 'inherit', 'boxShadow': '', 'fontStyle': 'normal', 'minHeight': '200px', 'textAlign': 'left', 'fontFamily': 'inherit', 'fontWeight': 'normal', 'borderRadius': '', 'backgroundColor': ''}, 
    'templateType': 'Report', 
    'documentTitle': 'Report Sheet', 
    'showSeparator': False, 
    'separatorStyle': {'color': '#9a1818', 'border': '1px solid #000000', 'margin': '10px 0', 'fontSize': '14px', 'fontStyle': 'normal', 'textAlign': 'left', 'fontFamily': 'inherit', 'fontWeight': 'normal'}, 
    'watermarkType': 'icon', 
    'watermarkText': 'AUA', 
    'watermarkImage': '', 
    'watermarkSize': 120, 
    'watermarkOpacity': 7, 
    'watermarkRotation': 0, 
    'containerStyle': {'color': '#333333', 'border': '1px solid #e5e7eb', 'margin': '0 auto', 'padding': '40px', 'fontSize': '1.2em', 'boxShadow': '', 'fontStyle': 'normal', 'textAlign': 'left', 'fontFamily': 'inherit', 'fontWeight': 'normal', 'borderRadius': '8px', 'backgroundColor': '#edf5f8'}, 
    'footerStyleObj': {'color': 'inherit', 'border': '', 'margin': 'auto 0 0 0', 'padding': '16px 0 0 0', 'fontSize': 'inherit', 'boxShadow': '', 'fontStyle': 'normal', 'textAlign': 'left', 'fontFamily': 'inherit', 'fontWeight': 'normal', 'borderRadius': '', 'backgroundColor': 'transparent'}, 
    'visibleSections': {'stamp': True, 'table': True, 'title': True, 'footer': True, 'header': True, 'remarks': True, 'signatures': True, 'studentInfo': True}, 
    'globalFontFamily': 'Arial', 
    'showStudentPhoto': False, 
    'studentPhotoStyle': {'width': '120px', 'height': '120px', 'opacity': 100, 'borderRadius': '8px'},
    'studentInfoFields': ['name', 'admissionNo', 'gender', 'positionInClass', 'term', 'classRoom'], 
    'studentInfoStyle': {'color': 'inherit', 'border': '1px solid #d1d5db', 'margin': '0 0 24px 0', 'padding': '16px', 'fontSize': '1em', 'boxShadow': '', 'fontStyle': 'normal', 'textAlign': 'left', 'fontFamily': 'inherit', 'fontWeight': 'normal', 'borderRadius': '4px', 'backgroundColor': '#edf5fa'}, 
    'primaryColor': '#1a3047'
}

ReportConfigPremium = {
    "templateType": "Report",
    "orientation": "portrait",
    "visibleSections": {
        "stamp": True,
        "table": True,
        "title": True,
        "footer": True,
        "header": True,
        "remarks": True,
        "signatures": True,
        "studentInfo": True
    },
    "primaryColor": "#0C1E36", # Deep prestige navy
    "borderColor": "#C5A059",  # Classic academic gold/brass accent
    "globalFontFamily": "Arial, sans-serif",
    
    "containerStyle": {
        "color": "#1A1A1A",
        "border": "2px solid #C5A059", # Structured frame border
        "margin": "0 auto",
        "padding": "48px 56px",
        "fontSize": "13px",
        "boxShadow": "0 4px 20px rgba(0, 0, 0, 0.06)",
        "fontStyle": "normal",
        "textAlign": "left",
        "fontFamily": "inherit",
        "fontWeight": "normal",
        "borderRadius": "4px",
        "backgroundColor": "#FFFFFF"
    },
    
    "watermarkType": "icon",
    "watermarkText": "LEARN",
    "watermarkImage": "",
    "watermarkOpacity": 5,
    "watermarkSize": 140,
    "watermarkRotation": -30,
    
    "logoPosition": "double",
    "headerStyle": "standard",
    
    # Header block style acting as a solid top banner
    "headerStyleObj": {
        "color": "#FFFFFF",
        "border": "",
        "margin": "-48px -56px 32px -56px", # Perfectly flush bleed to edges
        "padding": "32px 56px",
        "fontSize": "1em",
        "boxShadow": "",
        "fontStyle": "normal",
        "textAlign": "center",
        "fontFamily": '"Times New Roman", Times, serif',
        "fontWeight": "normal",
        "borderRadius": "4px 4px 0 0",
        "backgroundColor": "#0C1E36" # Solid deep navy banner top
    },
    
    "schoolNameStyle": {
        "color": "#FFFFFF",
        "border": "",
        "margin": "0 0 6px 0",
        "padding": "",
        "fontSize": "2.2em",
        "boxShadow": "",
        "fontStyle": "normal",
        "textAlign": "center",
        "fontFamily": "inherit",
        "fontWeight": "bold",
        "borderRadius": "",
        "backgroundColor": "transparent"
    },
    
    "schoolNameSecondaryStyle": {
        "color": "#C5A059", # Gold secondary text matching the screenshot
        "border": "",
        "margin": "0 0 4px 0",
        "padding": "",
        "fontSize": "1.1em",
        "boxShadow": "",
        "fontStyle": "italic",
        "textAlign": "center",
        "fontFamily": "Arial, sans-serif",
        "fontWeight": "bold",
        "borderRadius": "",
        "backgroundColor": "transparent"
    },
    
    "logoStyle": {
        "width": "75px",
        "height": "75px",
        "opacity": 100,
        "borderRadius": "6px",
        "border": "1px solid #C5A059"
    },
    
    "documentTitle": "Report Sheet",
    "titleStyle": {
        "color": "#0C1E36",
        "border": "",
        "margin": "0 auto 28px auto",
        "padding": "8px 44px",
        "fontSize": "1.1em",
        "boxShadow": "",
        "fontStyle": "normal",
        "textAlign": "center",
        "fontFamily": "inherit",
        "fontWeight": "bold",
        "borderRadius": "9999px", # Exact gold accent pill badge
        "backgroundColor": "#C5A059",
        "letterSpacing": "1px",
        "textTransform": "uppercase"
    },
    
    "showStudentPhoto": False,
    "studentPhotoStyle": {
        "width": "110px",
        "height": "110px",
        "opacity": 100,
        "borderRadius": "4px",
        "border": "1px solid #C5A059"
    },
    
    "showBarcode": True,
    "barcodeStyle": {
        "width": "100px",
        "height": "100px"
    },
    
    "studentInfoFields": [
        "name",
        "admissionNo",
        "gender",
        "positionInClass",
        "term",
        "classRoom"
    ],
    
    # Premium structured box container for meta fields
    "studentInfoStyle": {
        "color": "#0C1E36",
        "border": "1px solid #C5A059",
        "margin": "0 0 32px 0",
        "padding": "20px 24px",
        "fontSize": "1em",
        "boxShadow": "",
        "fontStyle": "normal",
        "textAlign": "left",
        "fontFamily": "inherit",
        "fontWeight": "normal",
        "borderRadius": "6px",
        "backgroundColor": "#FCFBF9" # Crisp premium ivory tint
    },
    
    "tableStyle": "bordered",
    "tableHeaderStyle": {
        "color": "#0C1E36",
        "border": "",
        "margin": "",
        "padding": "12px",
        "fontSize": "0.95em",
        "boxShadow": "",
        "fontStyle": "normal",
        "textAlign": "left",
        "fontFamily": "inherit",
        "fontWeight": "bold",
        "borderRadius": "",
        "backgroundColor":  "#C5A059" # Soft gray background layer for text readability
    },
    
    "tableBodyStyle": {
        "color": "#1A1A1A",
        "border": "",
        "margin": "",
        "padding": "12px",
        "fontSize": "0.95em",
        "boxShadow": "",
        "fontStyle": "normal",
        "textAlign": "left",
        "fontFamily": '"Times New Roman", Times, serif', # Highly professional traditional serif body data
        "fontWeight": "normal",
        "borderRadius": "",
        "backgroundColor": "#FFFFFF"
    },
    "tableCellPadding": "12px 14px",
    
    "showTextArea": False,
    "textAreaContent": "Enter your custom text here...",
    "textAreaStyle": {
        "color": "inherit",
        "border": "1px solid #C5A059",
        "margin": "0 0 24px 0",
        "padding": "16px",
        "fontSize": "1em",
        "boxShadow": "",
        "fontStyle": "normal",
        "minHeight": "150px",
        "textAlign": "left",
        "fontFamily": "inherit",
        "fontWeight": "normal",
        "borderRadius": "4px",
        "backgroundColor": "#FFFFFF"
    },
    
    "showRemarks": True,
    "remarksStyle": {
        "color": "#1A1A1A",
        "border": "1px solid #C5A059",
        "margin": "28px 0 0 0",
        "padding": "20px",
        "fontSize": "1em",
        "boxShadow": "",
        "fontStyle": "italic",
        "textAlign": "left",
        "fontFamily": '"Times New Roman", Times, serif',
        "fontWeight": "normal",
        "borderRadius": "4px",
        "backgroundColor": "#F4F4F6"
    },
    
    "signatures": [
        "REGISTRAR",
        "PRINCIPAL"
    ],
    "signatureStyle": {
        "color": "#0C1E36",
        "borderTop": "2px solid #0C1E36", # Clear professional signing baseline
        "margin": "64px 24px 0 24px",
        "padding": "8px 0 0 0",
        "fontSize": "0.9em",
        "boxShadow": "",
        "fontStyle": "normal",
        "textAlign": "center",
        "fontFamily": "inherit",
        "fontWeight": "bold",
        "borderRadius": "",
        "backgroundColor": ""
    },
    
    "footerStyleObj": {
        "color": "#FFFFFF",
        "border": "",
        "margin": "16px 0 0 0",
        "padding": "0",
        "fontSize": "0.85em",
        "boxShadow": "",
        "fontStyle": "normal",
        "textAlign": "center",
        "fontFamily": "inherit",
        "fontWeight": "normal",
        "borderRadius": "",
        "backgroundColor": "transparent"
    },
    
    "showStamp": True,
    "stampStyle": {
        "width": "110px",
        "height": "110px",
        "opacity": 35,
        "borderRadius": "50%",
        "border": "2px dashed #C5A059",
        "color": "#C5A059"
    },
    "stampX": 52,
    "stampY": 62,
    "stampRotation": 0,
    
    "skillsStyle": {
        "color": "#0C1E36",
        "fontSize": "1.1em",
        "fontStyle": "normal",
        "textAlign": "left",
        "fontFamily": "inherit",
        "fontWeight": "bold",
        "borderBottom": "2px solid #C5A059",
        "paddingBottom": "6px"
    },
    "showSeparator": False,
    "separatorStyle": {
        "color": "#C5A059",
        "border": "1px solid #C5A059",
        "margin": "12px 0",
        "fontSize": "14px",
        "fontStyle": "normal",
        "textAlign": "left",
        "fontFamily": "inherit",
        "fontWeight": "normal"
    }
}

ReportConfigGreenfield = {
    'stampX': 52, 
    'stampY': 62, 
    'showStamp': True, 
    'stampRotation': 0,
    'stampStyle': {
        'width': '110px', 
        'height': '110px', 
        'opacity': 40, 
        'borderRadius': '50%',
        'border': '2px dashed #c5a059',
        'color': '#c5a059'
    },
    
    'signatures': ['REGISTRAR', 'PRINCIPAL'],
    'signatureStyle': {
        'color': '#0c1e36', 
        'borderTop': '2px solid #0c1e36', 
        'margin': '64px 20px 0 20px', 
        'padding': '8px 0 0 0', 
        'fontSize': '0.85em', 
        'boxShadow': '', 
        'fontStyle': 'normal', 
        'textAlign': 'center', 
        'fontFamily': 'inherit', 
        'fontWeight': 'bold', 
        'borderRadius': '', 
        'backgroundColor': ''
    },
    
    'tableStyle': 'bordered',
    'borderColor': '#c5a059', 
    'tableCellPadding': '10px 12px', 
    
    'tableHeaderStyle': {
        'color': '#0c1e36', 
        'border': '', 
        'margin': '', 
        'padding': '10px', 
        'fontSize': '0.95em', 
        'boxShadow': '', 
        'fontStyle': 'normal', 
        'textAlign': 'left', 
        'fontFamily': 'inherit', 
        'fontWeight': 'bold', 
        'borderRadius': '', 
        'backgroundColor': '#f4f4f6'
    }, 
    
    'tableBodyStyle': {
        'color': '#000000', 
        'border': '', 
        'margin': '', 
        'padding': '10px', 
        'fontSize': '0.95em', 
        'boxShadow': '', 
        'fontStyle': 'normal', 
        'textAlign': 'left', 
        'fontFamily': '"Times New Roman", Times, serif', 
        'fontWeight': 'normal', 
        'borderRadius': '', 
        'backgroundColor': ''
    }, 
    
    # Matching the gold pill-shaped title badge exactly
    'titleStyle': {
        'color': '#0c1e36', 
        'border': '', 
        'margin': '0 auto 24px auto', 
        'padding': '8px 40px', 
        'fontSize': '1.1em', 
        'boxShadow': '', 
        'fontStyle': 'normal', 
        'textAlign': 'center', 
        'fontFamily': 'inherit', 
        'fontWeight': 'bold', 
        'borderRadius': '9999px', 
        'backgroundColor': '#c5a059',
        'letterSpacing': '0.5px'
    }, 
    
    'headerStyle': 'standard', 
    # The header block has a deep solid navy background spanning the top
    'headerStyleObj': {
        'color': '#ffffff', 
        'border': '', 
        'margin': '-48px -56px 32px -56px', 
        'padding': '32px 56px', 
        'fontSize': '1em', 
        'boxShadow': '', 
        'fontStyle': 'normal', 
        'textAlign': 'center', 
        'fontFamily': 'inherit', 
        'fontWeight': 'normal', 
        'borderRadius': '8px 8px 0 0', 
        'backgroundColor': '#0c1e36'
    }, 
    
    'schoolNameStyle': {
        'color': '#ffffff', 
        'border': '', 
        'margin': '0 0 4px 0', 
        'padding': '', 
        'fontSize': '2.2em', 
        'boxShadow': '', 
        'fontStyle': 'normal', 
        'textAlign': 'center', 
        'fontFamily': '"Times New Roman", Times, serif', 
        'fontWeight': 'bold', 
        'borderRadius': '', 
        'backgroundColor': 'transparent'
    }, 
    
    'schoolNameSecondaryStyle': {
        'color': '#c5a059', 
        'border': '', 
        'margin': '0 0 12px 0', 
        'padding': '', 
        'fontSize': '1.1em', 
        'boxShadow': '', 
        'fontStyle': 'italic', 
        'textAlign': 'center', 
        'fontFamily': 'inherit', 
        'fontWeight': '600', 
        'borderRadius': '', 
        'backgroundColor': ''
    },
    
    'logoPosition': 'left', 
    'logoStyle': {
        'width': '64px', 
        'height': '64px', 
        'opacity': 100, 
        'borderRadius': '8px',
        'border': '1px solid #c5a059'
    },
    
    'orientation': 'portrait', 
    'showBarcode': True, 
    'barcodeStyle': {
        'width': '80px', 
        'height': '80px',
        'border': '1px solid #c5a059',
        'padding': '8px'
    }, 
    
    'showRemarks': True, 
    # Light gray background tint container with thin gold border
    'remarksStyle': {
        'color': '#000000', 
        'border': '1px solid #c5a059', 
        'margin': '24px 0 0 0', 
        'padding': '20px', 
        'fontSize': '1em', 
        'boxShadow': '', 
        'fontStyle': 'italic', 
        'textAlign': 'left', 
        'fontFamily': '"Times New Roman", Times, serif', 
        'fontWeight': 'normal', 
        'borderRadius': '4px', 
        'backgroundColor': '#f4f4f6'
    }, 
    
    'skillsStyle': {
        'color': '#0c1e36', 
        'fontSize': '1.1em', 
        'fontStyle': 'normal', 
        'textAlign': 'left', 
        'fontFamily': 'inherit', 
        'fontWeight': 'bold',
        'borderBottom': '2px solid #c5a059',
        'paddingBottom': '4px',
        'textTransform': 'uppercase'
    }, 
    
    'showTextArea': False, 
    'textAreaContent': '', 
    'textAreaStyle': {}, 
    
    'templateType': 'Report', 
    'documentTitle': 'Report Sheet', 
    'showSeparator': False, 
    
    'watermarkType': 'icon', 
    'watermarkText': '', 
    'watermarkImage': '', 
    'watermarkSize': 150, 
    'watermarkOpacity': 5, 
    'watermarkRotation': 0, 
    
    # Outer sheet wrapper with clean alignment padding and gold outline border
    'containerStyle': {
        'color': '#0c1e36', 
        'border': '2px solid #c5a059', 
        'margin': '20px auto', 
        'padding': '48px 56px', 
        'fontSize': '13px', 
        'boxShadow': '0 4px 20px rgba(0, 0, 0, 0.08)', 
        'fontStyle': 'normal', 
        'textAlign': 'left', 
        'fontFamily': 'Arial, sans-serif', 
        'fontWeight': 'normal', 
        'borderRadius': '8px', 
        'backgroundColor': '#ffffff'
    }, 
    
    'footerStyleObj': {
        'color': '#ffffff', 
        'margin': '16px 0 0 0', 
        'padding': '0', 
        'fontSize': '0.8em', 
        'textAlign': 'center'
    }, 
    
    'visibleSections': {
        'stamp': True, 
        'table': True, 
        'title': True, 
        'footer': True, 
        'header': True, 
        'remarks': True, 
        'signatures': True, 
        'studentInfo': True
    }, 
    
    'globalFontFamily': 'Arial, sans-serif', 
    'showStudentPhoto': False, 
    'studentPhotoStyle': {'width': '100px', 'height': '100px', 'borderRadius': '4px'},
    
    'studentInfoFields': ['name', 'admissionNo', 'gender', 'positionInClass', 'term', 'classRoom'], 
    
    # Sharp gold card line container for the student data matrix
    'studentInfoStyle': {
        'color': '#000000', 
        'border': '1px solid #c5a059', 
        'margin': '0 0 32px 0', 
        'padding': '20px', 
        'fontSize': '1.05em', 
        'boxShadow': '', 
        'fontStyle': 'normal', 
        'textAlign': 'left', 
        'fontFamily': 'inherit', 
        'fontWeight': 'normal', 
        'borderRadius': '6px', 
        'backgroundColor': '#fafafa'
    }, 
    
    'primaryColor': '#0c1e36'
}