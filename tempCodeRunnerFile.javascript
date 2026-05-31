cat > /home/claude/testing_guide.js << 'ENDJS'
const {
  Document,Packer,Paragraph,TextRun,Table,TableRow,TableCell,
  HeadingLevel,AlignmentType,BorderStyle,WidthType,ShadingType,
  LevelFormat,PageBreak
} = require('docx');
const fs = require('fs');

const NAVY="1F3864",BLUE="2563EB",GREEN="166534",RED="991B1B",GRAY="374151",
      PURPLE="5B21B6",ORANGE="92400E";
const LTBLUE="EFF6FF",LTGRN="F0FDF4",LTYEL="FEFCE8",LTRED="FEF2F2",LTPUR="F5F3FF";

const brd=(c,s)=>({style:BorderStyle.SINGLE,size:s||1,color:c||"CCCCCC"});
const BORD={top:brd(),bottom:brd(),left:brd(),right:brd()};
const sp=(n)=>Array.from({length:n||1},()=>new Paragraph({children:[new TextRun("")],spacing:{before:40,after:40}}));
const pgB=()=>new Paragraph({children:[new PageBreak()]});

const h1=t=>new Paragraph({heading:HeadingLevel.HEADING_1,children:[new TextRun({text:t,bold:true,size:38,color:NAVY,font:"Arial"})],spacing:{before:280,after:130},border:{bottom:{style:BorderStyle.SINGLE,size:8,color:BLUE,space:4}}});
const h2=t=>new Paragraph({heading:HeadingLevel.HEADING_2,children:[new TextRun({text:t,bold:true,size:28,color:BLUE,font:"Arial"})],spacing:{before:200,after:80}});
const h3=t=>new Paragraph({heading:HeadingLevel.HEADING_3,children:[new TextRun({text:t,bold:true,size:24,color:GRAY,font:"Arial"})],spacing:{before:160,after:60}});
const p=(t,bold,col)=>new Paragraph({children:[new TextRun({text:t,size:22,font:"Arial",color:col||GRAY,bold:!!bold})],spacing:{before:50,after:50}});
const bul=t=>new Paragraph({numbering:{reference:"bullets",level:0},children:[new TextRun({text:t,size:22,font:"Arial",color:GRAY})],spacing:{before:36,after:36}});

function code(lines){
  return new Table({
    width:{size:9360,type:WidthType.DXA},columnWidths:[9360],
    rows:[new TableRow({children:[new TableCell({
      borders:{top:brd("93C5FD"),bottom:brd("93C5FD"),left:{style:BorderStyle.SINGLE,size:12,color:BLUE},right:brd("CCCCCC")},
      width:{size:9360,type:WidthType.DXA},shading:{fill:"EFF6FF",type:ShadingType.CLEAR},
      margins:{top:90,bottom:90,left:160,right:110},
      children:lines.map(l=>new Paragraph({children:[new TextRun({text:l,font:"Courier New",size:17,color:"1E3A5F"})],spacing:{before:0,after:0}}))
    })]})],
  });
}

function pathBanner(fpath,action){
  action=action||"FILE";
  return new Table({
    width:{size:9360,type:WidthType.DXA},columnWidths:[1800,7560],
    rows:[new TableRow({children:[
      new TableCell({borders:{top:brd("000000",0),bottom:brd("000000",0),left:brd("000000",0),right:brd("000000",0)},width:{size:1800,type:WidthType.DXA},shading:{fill:NAVY,type:ShadingType.CLEAR},margins:{top:90,bottom:90,left:120,right:60},children:[new Paragraph({children:[new TextRun({text:action,bold:true,size:18,font:"Arial",color:"FFFFFF"})],spacing:{before:0,after:0}})]}),
      new TableCell({borders:{top:brd("000000",0),bottom:brd("000000",0),left:brd("000000",0),right:brd("000000",0)},width:{size:7560,type:WidthType.DXA},shading:{fill:"1E3A5F",type:ShadingType.CLEAR},margins:{top:90,bottom:90,left:140,right:100},children:[new Paragraph({children:[new TextRun({text:fpath,bold:true,size:19,font:"Courier New",color:"93C5FD"})],spacing:{before:0,after:0}})]})
    ]})]
  });
}

function note(icon,title,body,fill,lc){
  fill=fill||LTBLUE; lc=lc||BLUE;
  return new Table({
    width:{size:9360,type:WidthType.DXA},columnWidths:[9360],
    rows:[new TableRow({children:[new TableCell({
      borders:{top:brd("93C5FD"),bottom:brd("93C5FD"),left:{style:BorderStyle.SINGLE,size:10,color:lc},right:{style:BorderStyle.NONE,size:0,color:"FFFFFF"}},
      width:{size:9360,type:WidthType.DXA},shading:{fill,type:ShadingType.CLEAR},
      margins:{top:90,bottom:90,left:140,right:140},
      children:[
        new Paragraph({children:[new TextRun({text:icon+" "+title,bold:true,size:22,font:"Arial",color:NAVY})],spacing:{after:36}}),
        new Paragraph({children:[new TextRun({text:body,size:21,font:"Arial",color:GRAY})],spacing:{after:0}})
      ]
    })]})],
  });
}

function secHdr(num,title,sub){
  return new Table({
    width:{size:9360,type:WidthType.DXA},columnWidths:[640,8720],
    rows:[new TableRow({children:[
      new TableCell({borders:{top:brd("000000",0),bottom:brd("000000",0),left:brd("000000",0),right:brd("000000",0)},width:{size:640,type:WidthType.DXA},shading:{fill:BLUE,type:ShadingType.CLEAR},margins:{top:90,bottom:90,left:80,right:60},children:[new Paragraph({alignment:AlignmentType.CENTER,children:[new TextRun({text:String(num),bold:true,size:32,font:"Arial",color:"FFFFFF"})],spacing:{before:0,after:0}})]}),
      new TableCell({borders:{top:brd("000000",0),bottom:brd("000000",0),left:brd("000000",0),right:brd("000000",0)},width:{size:8720,type:WidthType.DXA},shading:{fill:NAVY,type:ShadingType.CLEAR},margins:{top:90,bottom:90,left:180,right:100},children:[
        new Paragraph({children:[new TextRun({text:title,bold:true,size:26,font:"Arial",color:"FFFFFF"})],spacing:{before:0,after:sub?26:0}}),
        ...(sub?[new Paragraph({children:[new TextRun({text:sub,size:18,font:"Arial",color:"93C5FD",italics:true})],spacing:{before:0,after:0}})]:[])
      ]})
    ]})]
  });
}

function resultTable(rows){
  // rows = [[test, input, expected, pass/fail color]]
  var hdr=new TableRow({children:[
    new TableCell({borders:BORD,width:{size:400,type:WidthType.DXA},shading:{fill:NAVY,type:ShadingType.CLEAR},margins:{top:60,bottom:60,left:60,right:40},children:[new Paragraph({alignment:AlignmentType.CENTER,children:[new TextRun({text:"#",bold:true,size:18,font:"Arial",color:"FFFFFF"})]})] }),
    new TableCell({borders:BORD,width:{size:2200,type:WidthType.DXA},shading:{fill:NAVY,type:ShadingType.CLEAR},margins:{top:60,bottom:60,left:80,right:40},children:[new Paragraph({children:[new TextRun({text:"Test Name",bold:true,size:18,font:"Arial",color:"FFFFFF"})]})] }),
    new TableCell({borders:BORD,width:{size:2800,type:WidthType.DXA},shading:{fill:NAVY,type:ShadingType.CLEAR},margins:{top:60,bottom:60,left:80,right:40},children:[new Paragraph({children:[new TextRun({text:"Input / Action",bold:true,size:18,font:"Arial",color:"FFFFFF"})]})] }),
    new TableCell({borders:BORD,width:{size:2560,type:WidthType.DXA},shading:{fill:NAVY,type:ShadingType.CLEAR},margins:{top:60,bottom:60,left:80,right:40},children:[new Paragraph({children:[new TextRun({text:"Expected Result",bold:true,size:18,font:"Arial",color:"FFFFFF"})]})] }),
    new TableCell({borders:BORD,width:{size:400,type:WidthType.DXA},shading:{fill:NAVY,type:ShadingType.CLEAR},margins:{top:60,bottom:60,left:40,right:40},children:[new Paragraph({alignment:AlignmentType.CENTER,children:[new TextRun({text:"Status",bold:true,size:18,font:"Arial",color:"FFFFFF"})]})] }),
  ]});
  return new Table({
    width:{size:9360,type:WidthType.DXA},columnWidths:[400,2200,2800,2560,400],
    rows:[hdr].concat(rows.map((r,i)=>{
      var sh=i%2===0?"FFFFFF":"F8FAFC";
      return new TableRow({children:[
        new TableCell({borders:BORD,width:{size:400,type:WidthType.DXA},shading:{fill:sh,type:ShadingType.CLEAR},margins:{top:70,bottom:70,left:60,right:40},children:[new Paragraph({alignment:AlignmentType.CENTER,children:[new TextRun({text:String(i+1),bold:true,size:18,font:"Arial",color:NAVY})]})]}),
        new TableCell({borders:BORD,width:{size:2200,type:WidthType.DXA},shading:{fill:sh,type:ShadingType.CLEAR},margins:{top:70,bottom:70,left:80,right:40},children:[new Paragraph({children:[new TextRun({text:r[0],bold:true,size:18,font:"Arial",color:BLUE})]})]}),
        new TableCell({borders:BORD,width:{size:2800,type:WidthType.DXA},shading:{fill:sh,type:ShadingType.CLEAR},margins:{top:70,bottom:70,left:80,right:40},children:[new Paragraph({children:[new TextRun({text:r[1],size:18,font:"Arial",color:GRAY})]})]}),
        new TableCell({borders:BORD,width:{size:2560,type:WidthType.DXA},shading:{fill:sh,type:ShadingType.CLEAR},margins:{top:70,bottom:70,left:80,right:40},children:[new Paragraph({children:[new TextRun({text:r[2],size:18,font:"Arial",color:GRAY})]})]}),
        new TableCell({borders:BORD,width:{size:400,type:WidthType.DXA},shading:{fill:"F0FDF4",type:ShadingType.CLEAR},margins:{top:70,bottom:70,left:40,right:40},children:[new Paragraph({alignment:AlignmentType.CENTER,children:[new TextRun({text:"\u25A1",bold:true,size:18,font:"Arial",color:GREEN})]})]}),
      ]});
    }))
  });
}

function mlMetricTable(rows){
  var hdr=new TableRow({children:[
    new TableCell({borders:BORD,width:{size:2500,type:WidthType.DXA},shading:{fill:NAVY,type:ShadingType.CLEAR},margins:{top:60,bottom:60,left:100,right:60},children:[new Paragraph({children:[new TextRun({text:"Model",bold:true,size:18,font:"Arial",color:"FFFFFF"})]})] }),
    new TableCell({borders:BORD,width:{size:1720,type:WidthType.DXA},shading:{fill:NAVY,type:ShadingType.CLEAR},margins:{top:60,bottom:60,left:80,right:60},children:[new Paragraph({alignment:AlignmentType.CENTER,children:[new TextRun({text:"MAE (Rs.)",bold:true,size:18,font:"Arial",color:"FFFFFF"})]})] }),
    new TableCell({borders:BORD,width:{size:1720,type:WidthType.DXA},shading:{fill:NAVY,type:ShadingType.CLEAR},margins:{top:60,bottom:60,left:80,right:60},children:[new Paragraph({alignment:AlignmentType.CENTER,children:[new TextRun({text:"RMSE (Rs.)",bold:true,size:18,font:"Arial",color:"FFFFFF"})]})] }),
    new TableCell({borders:BORD,width:{size:1700,type:WidthType.DXA},shading:{fill:NAVY,type:ShadingType.CLEAR},margins:{top:60,bottom:60,left:80,right:60},children:[new Paragraph({alignment:AlignmentType.CENTER,children:[new TextRun({text:"R\u00b2 Score",bold:true,size:18,font:"Arial",color:"FFFFFF"})]})] }),
    new TableCell({borders:BORD,width:{size:1720,type:WidthType.DXA},shading:{fill:NAVY,type:ShadingType.CLEAR},margins:{top:60,bottom:60,left:80,right:60},children:[new Paragraph({alignment:AlignmentType.CENTER,children:[new TextRun({text:"Pass Threshold",bold:true,size:18,font:"Arial",color:"FFFFFF"})]})] }),
  ]});
  return new Table({
    width:{size:9360,type:WidthType.DXA},columnWidths:[2500,1720,1720,1700,1720],
    rows:[hdr].concat(rows.map((r,i)=>{
      var sh=i%2===0?"FFFFFF":"F8FAFC";
      var isGreen=r[4]==="PASS";
      return new TableRow({children:[
        new TableCell({borders:BORD,width:{size:2500,type:WidthType.DXA},shading:{fill:sh,type:ShadingType.CLEAR},margins:{top:70,bottom:70,left:100,right:60},children:[new Paragraph({children:[new TextRun({text:r[0],bold:true,size:18,font:"Arial",color:r[3]==="best"?GREEN:NAVY})]})]}),
        new TableCell({borders:BORD,width:{size:1720,type:WidthType.DXA},shading:{fill:sh,type:ShadingType.CLEAR},margins:{top:70,bottom:70,left:80,right:60},children:[new Paragraph({alignment:AlignmentType.CENTER,children:[new TextRun({text:r[1],size:18,font:"Arial",color:GRAY})]})]}),
        new TableCell({borders:BORD,width:{size:1720,type:WidthType.DXA},shading:{fill:sh,type:ShadingType.CLEAR},margins:{top:70,bottom:70,left:80,right:60},children:[new Paragraph({alignment:AlignmentType.CENTER,children:[new TextRun({text:r[2],size:18,font:"Arial",color:GRAY})]})]}),
        new TableCell({borders:BORD,width:{size:1700,type:WidthType.DXA},shading:{fill:r[3]==="best"?LTGRN:sh,type:ShadingType.CLEAR},margins:{top:70,bottom:70,left:80,right:60},children:[new Paragraph({alignment:AlignmentType.CENTER,children:[new TextRun({text:r[3]==="best"?r[3]+" \u2605":r[3],bold:r[3]==="best",size:18,font:"Arial",color:r[3]==="best"?GREEN:GRAY})]})]}),
        new TableCell({borders:BORD,width:{size:1720,type:WidthType.DXA},shading:{fill:isGreen?LTGRN:LTRED,type:ShadingType.CLEAR},margins:{top:70,bottom:70,left:80,right:60},children:[new Paragraph({alignment:AlignmentType.CENTER,children:[new TextRun({text:r[4],bold:true,size:18,font:"Arial",color:isGreen?GREEN:RED})]})]}),
      ]});
    }))
  });
}

// ─────────────────────────────────────────────────────────────
var C=[];

// COVER
C=C.concat(sp(4));
C.push(new Paragraph({alignment:AlignmentType.CENTER,children:[new TextRun({text:"USED CAR PRICE PREDICTION",bold:true,size:56,font:"Arial",color:NAVY})],spacing:{after:90}}));
C.push(new Paragraph({alignment:AlignmentType.CENTER,children:[new TextRun({text:"Complete Testing Guide",size:32,font:"Arial",color:BLUE})],spacing:{after:70}}));
C.push(new Paragraph({alignment:AlignmentType.CENTER,children:[new TextRun({text:"UI Testing  \u00b7  ML Model Validation  \u00b7  Prediction Accuracy  \u00b7  Edge Cases  \u00b7  Test Scripts",size:21,font:"Arial",color:GRAY,italics:true})],spacing:{after:260}}));

C.push(new Table({
  width:{size:9360,type:WidthType.DXA},columnWidths:[2340,2340,2340,2340],
  rows:[new TableRow({children:[
    new TableCell({borders:BORD,width:{size:2340,type:WidthType.DXA},shading:{fill:NAVY,type:ShadingType.CLEAR},margins:{top:110,bottom:110,left:100,right:100},children:[new Paragraph({alignment:AlignmentType.CENTER,children:[new TextRun({text:"UI Tests",bold:true,size:24,font:"Arial",color:"FFFFFF"})],spacing:{after:26}}),new Paragraph({alignment:AlignmentType.CENTER,children:[new TextRun({text:"All 12 screens",size:17,font:"Arial",color:"93C5FD"})]})] }),
    new TableCell({borders:BORD,width:{size:2340,type:WidthType.DXA},shading:{fill:BLUE,type:ShadingType.CLEAR},margins:{top:110,bottom:110,left:100,right:100},children:[new Paragraph({alignment:AlignmentType.CENTER,children:[new TextRun({text:"ML Tests",bold:true,size:24,font:"Arial",color:"FFFFFF"})],spacing:{after:26}}),new Paragraph({alignment:AlignmentType.CENTER,children:[new TextRun({text:"Model accuracy + R\u00b2",size:17,font:"Arial",color:"BFDBFE"})]})] }),
    new TableCell({borders:BORD,width:{size:2340,type:WidthType.DXA},shading:{fill:GREEN,type:ShadingType.CLEAR},margins:{top:110,bottom:110,left:100,right:100},children:[new Paragraph({alignment:AlignmentType.CENTER,children:[new TextRun({text:"Edge Cases",bold:true,size:24,font:"Arial",color:"FFFFFF"})],spacing:{after:26}}),new Paragraph({alignment:AlignmentType.CENTER,children:[new TextRun({text:"Invalid inputs",size:17,font:"Arial",color:"BBF7D0"})]})] }),
    new TableCell({borders:BORD,width:{size:2340,type:WidthType.DXA},shading:{fill:PURPLE,type:ShadingType.CLEAR},margins:{top:110,bottom:110,left:100,right:100},children:[new Paragraph({alignment:AlignmentType.CENTER,children:[new TextRun({text:"Test Scripts",bold:true,size:24,font:"Arial",color:"FFFFFF"})],spacing:{after:26}}),new Paragraph({alignment:AlignmentType.CENTER,children:[new TextRun({text:"Automated Python",size:17,font:"Arial",color:"DDD6FE"})]})] }),
  ]})]
}));
C=C.concat(sp(2));
C.push(new Paragraph({alignment:AlignmentType.CENTER,children:[new TextRun({text:"Mangalaparthi Sai Krishna  \u00b7  Final Year MCA  \u00b7  Osmania University",size:21,font:"Arial",color:"9CA3AF",italics:true})]}));
C.push(pgB());

// ═══════════════════════════════════════════════════════
// SECTION 1 — HOW TO RUN THE PROJECT FOR TESTING
// ═══════════════════════════════════════════════════════
C.push(secHdr(1,"How to Start the Project for Testing","Always do this first before running any test"));
C=C.concat(sp(1));
C.push(h2("1.1  Start the server"));
C.push(code([
"# Step 1: Open terminal and navigate to project",
"cd C:\\Users\\raghu\\OneDrive\\Desktop\\project_code\\used_car_project",
"",
"# Step 2: Activate virtual environment",
"venv\\Scripts\\activate",
"# You should see (venv) in the terminal",
"",
"# Step 3: Start Django development server",
"python manage.py runserver",
"",
"# Step 4: Open your browser and go to",
"# http://127.0.0.1:8000",
]));
C=C.concat(sp(1));
C.push(note("\ud83d\udca1","Keep this terminal open the whole time you are testing.",
  "Open a SECOND terminal window for running any Python test scripts.\nDo not press Ctrl+C in the first terminal — that stops the server.",
  LTYEL,"D97706"));
C.push(pgB());

// ═══════════════════════════════════════════════════════
// SECTION 2 — UI TESTING: ALL 12 SCREENS
// ═══════════════════════════════════════════════════════
C.push(secHdr(2,"UI Testing \u2014 All 12 Screens Step by Step","Open the browser and follow each step in order. Tick the box when it passes."));
C=C.concat(sp(1));

C.push(h2("2.1  Screen 1 \u2014 Landing Page  /"));
C.push(resultTable([
  ["Page loads","Visit http://127.0.0.1:8000","Navy hero with gradient, heading in white, yellow second line"],
  ["Hero buttons visible","Look at hero section","Green 'Get Started' + white outline 'How It Works' side by side"],
  ["4 feature cards","Scroll below hero","ML Powered, High Accuracy, Fast Prediction, Secure & Private — 4 white cards"],
  ["Card hover effect","Hover mouse over any card","Card lifts 6px upward with deeper shadow"],
  ["Dark mode toggle","Click moon icon (top-right navbar)","Page switches to dark: body #0F172A, cards #1E293B"],
  ["Refresh after dark mode","Press F5 after toggling dark","Page loads already dark — localStorage preference saved"],
  ["Get Started button","Click 'Get Started'","Redirects to /UserLogin/"],
]));
C=C.concat(sp(1));

C.push(h2("2.2  Screen 2 \u2014 Register  /UserRegister/"));
C.push(resultTable([
  ["Page layout","Visit /UserRegister/","White card centered, car icon top-right, yellow activation warning box"],
  ["All 4 fields visible","Look at form","Full Name, Email, Password, Confirm Password — all with labels"],
  ["Eye icon — Password","Click eye icon on Password field","Password text becomes visible. Icon changes to open eye."],
  ["Eye icon — Confirm","Click eye icon on Confirm Password","Same toggle behavior"],
  ["Input focus ring","Click inside Email field","Blue glow ring appears around the input"],
  ["Empty form submit","Click Register without filling","Browser required-field validation stops submission"],
  ["Password mismatch","Enter different passwords, submit","Red error box: 'Passwords do not match'"],
  ["Duplicate email","Register same email twice","Error: 'Email already registered. Please login.'"],
  ["Valid registration","Fill all fields correctly","RegistrationSuccess page — yellow pending activation box shown"],
]));
C=C.concat(sp(1));

C.push(h2("2.3  Screen 3 \u2014 Login  /UserLogin/"));
C.push(resultTable([
  ["Page layout","Visit /UserLogin/","White card, blue shield icon in circle, 'Welcome Back!' heading"],
  ["Eye icon","Click eye on Password field","Password revealed. Icon changes."],
  ["Wrong credentials","Submit wrong email/password","Red error: 'Invalid email or password. Please try again.'"],
  ["Inactive account","Login before admin activates","Error: 'Account not activated. Please contact the admin.'"],
  ["Valid login","Login with activated account","Session set, redirects to /UserHome/"],
  ["Navbar after login","Check navbar","Shows: Dashboard, Dataset, Train, Predict, History, Compare, red Logout button"],
]));
C=C.concat(sp(1));

C.push(h2("2.4  Screen 4 \u2014 User Dashboard  /UserHome/"));
C.push(resultTable([
  ["Welcome banner","Visit /UserHome/ after login","Light-blue banner: 'Welcome back, [Name]' + car SVG icon right"],
  ["4 action cards","Look at cards row","Train Models, Predict Price, View History, About Project — all with colored icons"],
  ["Stat tiles","Look at bottom row","Total Predictions, Models Trained, Best Model, Accuracy — 4 tiles"],
  ["Train Models card","Click 'Go to Training' button","Navigates to /training/"],
  ["Predict Now card","Click 'Predict Now' button","Navigates to /prediction/"],
  ["View History card","Click 'View History' button","Navigates to /prediction_history/"],
  ["No login redirect","Open /UserHome/ in incognito","Redirects to /UserLogin/ — session guard working"],
]));
C=C.concat(sp(1));

C.push(h2("2.5  Screens 5 & 6 \u2014 Model Training  /training/"));
C.push(resultTable([
  ["Before training","Visit /training/","Gear icon, 'Model Training' heading, yellow warning, blue Start Training button"],
  ["Button click","Click Start Training","Button text changes to 'Training\u2026 please wait', becomes disabled/gray"],
  ["Training completes","Wait 1-3 minutes","Green success banner + comparison table + 3 charts appear"],
  ["Results table","Check comparison table","All 4 models listed with MAE, RMSE, R\u00b2 — best model row in green bold"],
  ["R\u00b2 bar chart","Check first chart image","4 colored bars, taller = better — Random Forest should be tallest"],
  ["Feature importance chart","Check second chart","Horizontal bars showing which features matter most"],
  ["Actual vs Predicted","Check third chart","Scatter plot: points close to diagonal red line = good model"],
  ["Predict button after","Click 'Predict a Price' button","Navigates to /prediction/"],
]));
C=C.concat(sp(1));

C.push(h2("2.6  Screen 7 \u2014 Predict Price Form  /prediction/"));
C.push(resultTable([
  ["Form layout","Visit /prediction/","2-column grid of 10 dropdowns/inputs, blue Predict Price button"],
  ["All dropdowns","Click each dropdown","Brand: 14 options. Fuel: 5 options. Transmission: 2 options. Seller: 3 options."],
  ["No model trained","Visit before training","Red error: 'Model not trained yet. Go to Train Model page first.'"],
  ["Empty KM Driven","Submit with KM field empty","Red error box: 'KM Driven must be a number. No commas or letters.'"],
  ["KM too low","Enter km_driven = 100","Error: 'KM driven is too low. Minimum 500 km.'"],
  ["KM too high","Enter km_driven = 999999","Error: 'KM driven too high. Max 5,00,000.'"],
  ["Error preserves values","Submit with error, check form","Dropdowns still show previously selected values (form_data preserved)"],
  ["Button disable","Click Predict Price","Button shows 'Calculating\u2026', disables — prevents double submission"],
  ["Valid submission","Fill valid data, submit","Redirects to prediction result page (Screen 8)"],
]));
C=C.concat(sp(1));

C.push(h2("2.7  Screen 8 \u2014 Prediction Result  /prediction/ (POST)"));
C.push(resultTable([
  ["Green result card","Check after valid prediction","Large green gradient card with big \u20b9 price amount in white bold"],
  ["Price range","Check below main price","Range: \u20b9[lower] \u2014 \u20b9[upper] (approx \u00b110% of predicted)"],
  ["Price tag badge","Check inside green card","Shows 'Cheap' (green), 'Fair' (amber), or 'Expensive' (red) badge"],
  ["Similar cars table","Scroll below result card","Table with 5 real CarDekho rows for same brand + fuel"],
  ["Car details section","Scroll further down","All submitted values listed in 2-column grid with bullet points"],
  ["Feature importance chart","Check chart on result page","Bar chart shows which car features affected the price most"],
  ["Predict Another button","Click 'Predict Another Car'","Returns to empty /prediction/ form"],
  ["View History button","Click 'View My History'","Navigates to /prediction_history/"],
]));
C=C.concat(sp(1));

C.push(h2("2.8  Screen 9 \u2014 Prediction History  /prediction_history/"));
C.push(resultTable([
  ["Stat cards","Visit /prediction_history/","4 colored cards: Total (blue), Avg (green), Highest (orange), Lowest (purple)"],
  ["History table","Check table below cards","Each row: Brand, Age, KM, Fuel, Trans, Price (green), Date, Delete button"],
  ["Delete a row","Click Delete \u2192 Confirm","Row disappears. Total count on stat card decreases by 1."],
  ["Pagination","Make 6+ predictions then visit","Page 1 shown, next arrow appears, page 2 button exists"],
  ["Page 2","Click page 2 button","Second set of 5 records loads, page 2 button highlighted blue"],
  ["Empty state","Visit before any predictions","Clipboard icon + 'No predictions yet' + 'Make First Prediction' button"],
  ["Brand link click","Click Brand name in table","Navigates to /history_detail/<id>/ — detail page"],
]));
C=C.concat(sp(1));

C.push(h2("2.9  Screen 10 \u2014 Admin Dashboard  /AdminHome/"));
C.push(resultTable([
  ["Admin login","Visit /AdminLogin/, login admin/admin123","Redirects to /AdminHome/ with sidebar + stat cards"],
  ["Sidebar nav","Check left sidebar","Dashboard, Users, Trainings, History, Logout links — navy background"],
  ["Active link","Check Dashboard link in sidebar","Has blue left border + slightly lighter background"],
  ["4 stat cards","Check main content area","Total Users, Total Predictions, Models Trained, Best Model — correct numbers"],
  ["Recent Users table","Check right section","Up to 5 latest users. Active badge = green. Inactive = red."],
  ["Recent Predictions table","Check right section","Up to 5 latest predictions with price in green bold"],
  ["Activate user","Click Activate next to inactive user","Page refreshes. Status changes to Active (green badge)."],
  ["Admin guard","Open /AdminHome/ without admin session","Redirects to /AdminLogin/"],
]));
C=C.concat(sp(1));

C.push(h2("2.10  Screen 11 \u2014 History Detail  /history_detail/<id>/"));
C.push(resultTable([
  ["Access via link","Click Brand name in history table","Detail card loads with '← Back to History' link at top"],
  ["Card header","Check top of white card","'Prediction Details' heading left, 'Print' button right"],
  ["Detail table","Check table rows","All fields: Brand, Age, KM, Fuel, Trans, Mileage, Engine, Power, Seats"],
  ["Predicted price box","Check bottom of card","Green highlight box with large \u20b9 amount + timestamp below"],
  ["Print button","Click Print","Browser print dialog opens"],
  ["Back link","Click '\u2190 Back to History'","Returns to /prediction_history/ list"],
]));
C=C.concat(sp(1));

C.push(h2("2.11  Screen 12 \u2014 About Project  /about/"));
C.push(resultTable([
  ["Intro card","Visit /about/","Description text left, 3 icon boxes (car, chart, gear) right"],
  ["4 info cards","Check cards row","Dataset, Preprocessing, ML Models, Best Model — colored icon circles"],
  ["Best Model R\u00b2","Check Best Model card","Shows actual R\u00b2 from training results e.g. R\u00b2 = 0.9355"],
  ["Tech badges","Check bottom section","Python (yellow), Pandas (blue), scikit-learn (red), XGBoost (green), Django (emerald)"],
  ["Dashboard link","Click 'Learn More' on UserHome","Navigates to /about/"],
]));
C.push(pgB());

// ═══════════════════════════════════════════════════════
// SECTION 3 — ML MODEL TESTING
// ═══════════════════════════════════════════════════════
C.push(secHdr(3,"ML Model Testing \u2014 Verify the Model is Working Correctly","Run these checks after training to confirm the best model is selected and gives accurate results"));
C=C.concat(sp(1));

C.push(h2("3.1  What Good Metrics Look Like"));
C.push(p("After training, check the results table on Screen 6. Use this reference to know if your model is good:"));
C=C.concat(sp(1));
C.push(mlMetricTable([
  ["Linear Regression","~2,00,000","~3,30,000","0.70","PASS"],
  ["Ridge Regression","~2,00,000","~3,30,000","0.70","PASS"],
  ["Lasso Regression","~2,00,000","~3,30,000","0.70","PASS"],
  ["Random Forest (best)","~80,000","~1,50,000","best","PASS"],
]));
C=C.concat(sp(1));
C.push(note("\u2705","Pass/Fail thresholds:",
  "R\u00b2 above 0.70 = acceptable model\nR\u00b2 above 0.85 = good model\nR\u00b2 above 0.90 = excellent model\n\nMAE below Rs.1,00,000 = good (average error less than 1 lakh)\nIf ALL 4 models show R\u00b2 below 0.60, your dataset may have issues — check car_data.csv",
  LTGRN,GREEN));
C=C.concat(sp(1));

C.push(h2("3.2  Manual ML Test Script"));
C.push(p("Create this file and run it to test the model directly without the browser:"));
C=C.concat(sp(1));
C.push(pathBanner("used_car_project/test_model.py","CREATE NEW FILE"));
C=C.concat(sp(1));
C.push(code([
"# test_model.py",
"# Run from project root: python test_model.py",
"# Tests that the ML model loads and gives reasonable predictions",
"",
"import sys, os",
"sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))",
"",
"print('='*60)",
"print('USED CAR PRICE PREDICTION - ML MODEL TEST')",
"print('='*60)",
"",
"# ── Test 1: Check model files exist ─────────────────────────",
"print('\\n[TEST 1] Checking model files exist...')",
"required_files = [",
"    'models/best_model.pkl',",
"    'models/scaler.pkl',",
"    'models/label_encoders.pkl',",
"    'models/feature_names.pkl',",
"    'models/training_results.pkl',",
"]",
"all_exist = True",
"for f in required_files:",
"    exists = os.path.exists(f)",
"    status = 'PASS' if exists else 'FAIL - File missing!'",
"    print(f'  {status}: {f}')",
"    if not exists: all_exist = False",
"if not all_exist:",
"    print('  > Go to /training/ and click Start Training first.')",
"    sys.exit(1)",
"print('  All model files found.')",
"",
"# ── Test 2: Load model and check type ───────────────────────",
"print('\\n[TEST 2] Loading best model...')",
"import joblib",
"try:",
"    model    = joblib.load('models/best_model.pkl')",
"    scaler   = joblib.load('models/scaler.pkl')",
"    encoders = joblib.load('models/label_encoders.pkl')",
"    features = joblib.load('models/feature_names.pkl')",
"    results  = joblib.load('models/training_results.pkl')",
"    print(f'  PASS: Model type = {type(model).__name__}')",
"    print(f'  PASS: Feature count = {len(features)}')",
"    print(f'  PASS: Encoders for: {list(encoders.keys())}')",
"except Exception as e:",
"    print(f'  FAIL: Could not load models - {e}')",
"    sys.exit(1)",
"",
"# ── Test 3: Print training metrics ──────────────────────────",
"print('\\n[TEST 3] Training metrics for all models:')",
"best_name = max(results, key=lambda x: results[x]['R2'])",
"for name, m in results.items():",
"    marker = ' <-- BEST' if name == best_name else ''",
"    r2_ok  = 'PASS' if m['R2'] >= 0.70 else 'FAIL (R2 too low)'",
"    print(f'  {name}')",
"    print(f'    MAE:  Rs.{m[\"MAE\"]:,.0f}')",
"    print(f'    RMSE: Rs.{m[\"RMSE\"]:,.0f}')",
"    print(f'    R2:   {m[\"R2\"]} | {r2_ok}{marker}')",
"",
"# ── Test 4: Predict with known inputs and check range ────────",
"print('\\n[TEST 4] Making test predictions...')",
"from ml_pipeline.predict import predict_price",
"",
"test_cars = [",
"    {",
"        'name': 'New Maruti Petrol (should be LOW price)',",
"        'data': {",
"            'brand':'Maruti','vehicle_age':'2','km_driven':'20000',",
"            'seller_type':'Individual','fuel_type':'Petrol',",
"            'transmission':'Manual','mileage':'23.0',",
"            'engine':'998','max_power':'67.0','seats':'5',",
"        },",
"        'min_expected': 200000,   # Rs.2 lakh",
"        'max_expected': 700000,   # Rs.7 lakh",
"    },",
"    {",
"        'name': 'Old Diesel High KM (should be LOWER price)',",
"        'data': {",
"            'brand':'Hyundai','vehicle_age':'10','km_driven':'150000',",
"            'seller_type':'Individual','fuel_type':'Diesel',",
"            'transmission':'Manual','mileage':'19.0',",
"            'engine':'1396','max_power':'89.0','seats':'5',",
"        },",
"        'min_expected': 150000,   # Rs.1.5 lakh",
"        'max_expected': 600000,   # Rs.6 lakh",
"    },",
"    {",
"        'name': 'New Automatic Petrol (should be HIGHER price)',",
"        'data': {",
"            'brand':'Honda','vehicle_age':'1','km_driven':'10000',",
"            'seller_type':'Dealer','fuel_type':'Petrol',",
"            'transmission':'Automatic','mileage':'17.0',",
"            'engine':'1498','max_power':'118.0','seats':'5',",
"        },",
"        'min_expected': 800000,   # Rs.8 lakh",
"        'max_expected': 2500000,  # Rs.25 lakh",
"    },",
"]",
"",
"all_passed = True",
"for car in test_cars:",
"    try:",
"        result = predict_price(car['data'])",
"        price  = result['predicted']",
"        in_range = car['min_expected'] <= price <= car['max_expected']",
"        status = 'PASS' if in_range else 'FAIL (out of expected range)'",
"        if not in_range: all_passed = False",
"        print(f'  {car[\"name\"]}')",
"        print(f'    Predicted: Rs.{price:,.0f}')",
"        print(f'    Expected:  Rs.{car[\"min_expected\"]:,} to Rs.{car[\"max_expected\"]:,}')",
"        print(f'    Result:    {status}')",
"    except Exception as e:",
"        print(f'  FAIL: {car[\"name\"]} - Error: {e}')",
"        all_passed = False",
"",
"# ── Test 5: Sanity check — newer car > older car ─────────────",
"print('\\n[TEST 5] Sanity check: newer car should cost more...')",
"try:",
"    new_car = predict_price({",
"        'brand':'Maruti','vehicle_age':'1','km_driven':'10000',",
"        'seller_type':'Individual','fuel_type':'Petrol',",
"        'transmission':'Manual','mileage':'22.0',",
"        'engine':'998','max_power':'67.0','seats':'5',",
"    })",
"    old_car = predict_price({",
"        'brand':'Maruti','vehicle_age':'12','km_driven':'180000',",
"        'seller_type':'Individual','fuel_type':'Petrol',",
"        'transmission':'Manual','mileage':'22.0',",
"        'engine':'998','max_power':'67.0','seats':'5',",
"    })",
"    new_price = new_car['predicted']",
"    old_price = old_car['predicted']",
"    passed    = new_price > old_price",
"    print(f'  New car (1 yr, 10k km): Rs.{new_price:,.0f}')",
"    print(f'  Old car (12yr,180k km): Rs.{old_price:,.0f}')",
"    print(f'  New > Old: {\"PASS\" if passed else \"FAIL (model logic problem)\"}')",
"    if not passed: all_passed = False",
"except Exception as e:",
"    print(f'  FAIL: {e}')",
"    all_passed = False",
"",
"# ── Test 6: High KM car < Low KM car (same everything else) ──",
"print('\\n[TEST 6] Sanity check: low KM car should cost more...')",
"try:",
"    base = {'brand':'Toyota','vehicle_age':'5','seller_type':'Individual',",
"            'fuel_type':'Petrol','transmission':'Manual',",
"            'mileage':'18.0','engine':'1496','max_power':'103.0','seats':'5'}",
"    low_km  = {**base,'km_driven':'30000'}",
"    high_km = {**base,'km_driven':'200000'}",
"    r_low  = predict_price(low_km)['predicted']",
"    r_high = predict_price(high_km)['predicted']",
"    passed = r_low > r_high",
"    print(f'  30,000 km car:  Rs.{r_low:,.0f}')",
"    print(f'  2,00,000 km car: Rs.{r_high:,.0f}')",
"    print(f'  Low KM > High KM: {\"PASS\" if passed else \"FAIL (model logic problem)\"}')",
"    if not passed: all_passed = False",
"except Exception as e:",
"    print(f'  FAIL: {e}')",
"    all_passed = False",
"",
"# ── SUMMARY ──────────────────────────────────────────────────",
"print('\\n' + '='*60)",
"if all_passed:",
"    print('ALL TESTS PASSED - Model is working correctly!')",
"else:",
"    print('SOME TESTS FAILED - See output above for details.')",
"print('='*60)",
]));
C=C.concat(sp(1));

C.push(h2("3.3  How to Run the Test Script"));
C.push(code([
"# Open a NEW terminal (keep Django server running in the other one)",
"cd C:\\Users\\raghu\\OneDrive\\Desktop\\project_code\\used_car_project",
"venv\\Scripts\\activate",
"",
"# Run the test",
"python test_model.py",
"",
"# Expected output when everything passes:",
"# ============================================================",
"# USED CAR PRICE PREDICTION - ML MODEL TEST",
"# ============================================================",
"# [TEST 1] Checking model files exist...",
"#   PASS: models/best_model.pkl",
"#   PASS: models/scaler.pkl",
"#   ... (all 5 files)",
"# [TEST 2] Loading best model...",
"#   PASS: Model type = RandomForestRegressor",
"#   PASS: Feature count = 10",
"# [TEST 3] Training metrics...",
"#   Random Forest   R2: 0.9355  PASS <-- BEST",
"# [TEST 4] Making test predictions...",
"#   New Maruti Petrol   Rs.4,20,000  PASS",
"#   Old Diesel High KM  Rs.2,80,000  PASS",
"#   New Automatic       Rs.12,50,000 PASS",
"# [TEST 5] Newer > Older: PASS",
"# [TEST 6] Low KM > High KM: PASS",
"# ALL TESTS PASSED",
]));
C.push(pgB());

// ═══════════════════════════════════════════════════════
// SECTION 4 — TRAINING METRICS VALIDATION
// ═══════════════════════════════════════════════════════
C.push(secHdr(4,"Training Metrics Validation Script","Verify R\u00b2, MAE and RMSE are within acceptable range automatically"));
C=C.concat(sp(1));
C.push(pathBanner("used_car_project/test_metrics.py","CREATE NEW FILE"));
C=C.concat(sp(1));
C.push(code([
"# test_metrics.py",
"# Run: python test_metrics.py",
"# Checks that training results meet minimum quality standards",
"",
"import joblib, os, sys",
"",
"print('='*55)",
"print('ML METRICS VALIDATION')",
"print('='*55)",
"",
"if not os.path.exists('models/training_results.pkl'):",
"    print('FAIL: training_results.pkl not found.')",
"    print('  Go to /training/ and click Start Training first.')",
"    sys.exit(1)",
"",
"results = joblib.load('models/training_results.pkl')",
"",
"# Thresholds",
"MIN_R2   = 0.70    # minimum acceptable R2",
"GOOD_R2  = 0.85    # good R2",
"EXCEL_R2 = 0.90    # excellent R2",
"MAX_MAE  = 200000  # maximum acceptable MAE (Rs.2 lakh)",
"",
"all_pass = True",
"best_model = max(results, key=lambda x: results[x]['R2'])",
"",
"for name, m in results.items():",
"    r2   = m['R2']",
"    mae  = m['MAE']",
"    rmse = m['RMSE']",
"    is_best = (name == best_model)",
"",
"    r2_status  = 'PASS' if r2  >= MIN_R2  else 'FAIL'",
"    mae_status = 'PASS' if mae <= MAX_MAE else 'FAIL'",
"    if r2_status == 'FAIL' or mae_status == 'FAIL':",
"        all_pass = False",
"",
"    if r2 >= EXCEL_R2:  quality = 'EXCELLENT'",
"    elif r2 >= GOOD_R2: quality = 'GOOD'",
"    else:               quality = 'ACCEPTABLE'",
"",
"    prefix = '>> BEST MODEL <<' if is_best else ''",
"    print(f'\\n  {name}  {prefix}')",
"    print(f'    R2 Score: {r2}  ({r2_status}) - {quality}')",
"    print(f'    MAE:      Rs.{mae:,.0f}  ({mae_status})')",
"    print(f'    RMSE:     Rs.{rmse:,.0f}')",
"",
"print(f'\\n  Best Model Selected: {best_model}')",
"print(f'  Best R2: {results[best_model][\"R2\"]}')",
"print(f'\\n  Min R2 threshold:  {MIN_R2}')",
"print(f'  Max MAE threshold: Rs.{MAX_MAE:,}')",
"print()",
"if all_pass:",
"    print('ALL METRICS PASS - Training was successful!')",
"else:",
"    print('SOME METRICS FAILED - Consider retraining or checking dataset.')",
"    print('Tips:')",
"    print('  1. Make sure car_data.csv has at least 100+ rows')",
"    print('  2. Check for missing values in selling_price column')",
"    print('  3. Try removing extreme outliers from the dataset')",
"print('='*55)",
]));
C.push(pgB());

// ═══════════════════════════════════════════════════════
// SECTION 5 — EDGE CASE TESTING
// ═══════════════════════════════════════════════════════
C.push(secHdr(5,"Edge Case Testing \u2014 What Happens with Bad Input","Test these manually in the browser to confirm all error handling is working"));
C=C.concat(sp(1));

C.push(h2("5.1  Prediction Form Edge Cases (Screen 7)"));
C.push(resultTable([
  ["KM = 0","Enter 0 in Km Driven field, submit","Error: 'KM driven is too low. Minimum 500 km.'"],
  ["KM = letters","Type 'abcde' in Km Driven, submit","Error: 'KM Driven must be a number. No commas or letters.'"],
  ["KM with comma","Type '1,00,000' in Km Driven, submit","Error: same as above — commas not allowed"],
  ["No model trained","Delete models/ folder, then submit","Error: 'Model not trained yet. Go to Train Model page first.'"],
  ["Very new car","Vehicle Age=1, KM=5000, submit","Price should be HIGH (6-20 lakh range)"],
  ["Very old car","Vehicle Age=15, KM=200000, submit","Price should be LOW (1-4 lakh range)"],
  ["Electric car","Fuel Type=Electric, submit","Prediction works — no crash (even with limited data)"],
  ["All dropdowns minimum","Select lowest option everywhere","No crash — returns a low price estimate"],
]));
C=C.concat(sp(1));

C.push(h2("5.2  Authentication Edge Cases"));
C.push(resultTable([
  ["Access dashboard without login","Open /UserHome/ in incognito","Redirects to /UserLogin/"],
  ["Access training without login","Open /training/ in incognito","Redirects to /UserLogin/"],
  ["Access prediction without login","Open /prediction/ in incognito","Redirects to /UserLogin/"],
  ["Access history without login","Open /prediction_history/ in incognito","Redirects to /UserLogin/"],
  ["Access admin without session","Open /AdminHome/ without admin login","Redirects to /AdminLogin/"],
  ["Wrong admin password","Login with wrong admin password","Error: 'Invalid credentials'"],
  ["User tries admin URL","Login as user, visit /AdminHome/","Redirects to /AdminLogin/ — session isolation working"],
  ["Delete other user's prediction","Modify URL /delete_prediction/1/ as user2","Only deletes if prediction belongs to logged-in user"],
]));
C=C.concat(sp(1));

C.push(h2("5.3  Registration Edge Cases"));
C.push(resultTable([
  ["Empty name","Submit with blank Full Name","Browser required-field validation stops it"],
  ["Invalid email","Submit with 'notanemail'","Browser email validation stops it"],
  ["Short password","Enter 3-char password","Django form error: password too short"],
  ["Passwords mismatch","Enter different passwords","Error: 'Passwords do not match'"],
  ["Already registered email","Register same email twice","Error: 'Email already registered. Please login.'"],
  ["Login before activation","Register then immediately login","Error: 'Account not activated. Please contact the admin.'"],
]));
C.push(pgB());

// ═══════════════════════════════════════════════════════
// SECTION 6 — AUTOMATED DJANGO TEST
// ═══════════════════════════════════════════════════════
C.push(secHdr(6,"Automated Django Tests (tests.py)","Add these to users/tests.py to test views and models programmatically"));
C=C.concat(sp(1));
C.push(pathBanner("used_car_project/users/tests.py","CREATE OR REPLACE FILE"));
C=C.concat(sp(1));
C.push(code([
"# users/tests.py",
"# Run with: python manage.py test users",
"from django.test import TestCase, Client",
"from .models import UserProfile, PredictionHistory",
"",
"class UserModelTest(TestCase):",
"",
"    def test_create_user(self):",
"        \"\"\"Test that a UserProfile can be created\"\"\"",
"        user = UserProfile.objects.create(",
"            name='Test User',",
"            email='test@test.com',",
"            password='test123',",
"            is_active=False",
"        )",
"        self.assertEqual(user.name, 'Test User')",
"        self.assertFalse(user.is_active)",
"        print('PASS: UserProfile created with is_active=False')",
"",
"    def test_user_activation(self):",
"        \"\"\"Test that a user can be activated\"\"\"",
"        user = UserProfile.objects.create(",
"            name='Activate Me',",
"            email='activate@test.com',",
"            password='pass123',",
"            is_active=False",
"        )",
"        user.is_active = True",
"        user.save()",
"        updated = UserProfile.objects.get(email='activate@test.com')",
"        self.assertTrue(updated.is_active)",
"        print('PASS: User activation works')",
"",
"    def test_duplicate_email_rejected(self):",
"        \"\"\"Test that duplicate emails raise an error\"\"\"",
"        UserProfile.objects.create(",
"            name='First', email='dup@test.com',",
"            password='pass', is_active=True",
"        )",
"        from django.db import IntegrityError",
"        with self.assertRaises(IntegrityError):",
"            UserProfile.objects.create(",
"                name='Second', email='dup@test.com',",
"                password='pass', is_active=True",
"            )",
"        print('PASS: Duplicate email correctly rejected')",
"",
"",
"class ViewAccessTest(TestCase):",
"",
"    def setUp(self):",
"        self.client = Client()",
"        self.user = UserProfile.objects.create(",
"            name='SK', email='sk@test.com',",
"            password='pass123', is_active=True",
"        )",
"",
"    def test_index_loads(self):",
"        \"\"\"Landing page must return 200\"\"\"",
"        resp = self.client.get('/')",
"        self.assertEqual(resp.status_code, 200)",
"        print('PASS: Landing page loads (200)')",
"",
"    def test_login_page_loads(self):",
"        resp = self.client.get('/UserLogin/')",
"        self.assertEqual(resp.status_code, 200)",
"        print('PASS: Login page loads (200)')",
"",
"    def test_register_page_loads(self):",
"        resp = self.client.get('/UserRegister/')",
"        self.assertEqual(resp.status_code, 200)",
"        print('PASS: Register page loads (200)')",
"",
"    def test_dashboard_redirects_without_login(self):",
"        \"\"\"UserHome must redirect to login if not logged in\"\"\"",
"        resp = self.client.get('/UserHome/')",
"        self.assertEqual(resp.status_code, 302)",
"        self.assertIn('UserLogin', resp['Location'])",
"        print('PASS: Dashboard redirects without login (302)')",
"",
"    def test_prediction_redirects_without_login(self):",
"        resp = self.client.get('/prediction/')",
"        self.assertEqual(resp.status_code, 302)",
"        print('PASS: Prediction redirects without login (302)')",
"",
"    def test_training_redirects_without_login(self):",
"        resp = self.client.get('/training/')",
"        self.assertEqual(resp.status_code, 302)",
"        print('PASS: Training redirects without login (302)')",
"",
"    def test_wrong_login_rejected(self):",
"        \"\"\"Wrong password must not create a session\"\"\"",
"        resp = self.client.post('/UserLoginCheck/', {",
"            'email': 'sk@test.com',",
"            'password': 'wrongpassword'",
"        })",
"        self.assertNotIn('user_id', self.client.session)",
"        print('PASS: Wrong password correctly rejected')",
"",
"    def test_correct_login_sets_session(self):",
"        \"\"\"Correct login must set user_id in session\"\"\"",
"        resp = self.client.post('/UserLoginCheck/', {",
"            'email': 'sk@test.com',",
"            'password': 'pass123'",
"        })",
"        self.assertIn('user_id', self.client.session)",
"        print('PASS: Correct login sets session')",
"",
"",
"class PredictionHistoryTest(TestCase):",
"",
"    def setUp(self):",
"        self.user = UserProfile.objects.create(",
"            name='SK', email='sk2@test.com',",
"            password='pass123', is_active=True",
"        )",
"",
"    def test_create_prediction_history(self):",
"        \"\"\"PredictionHistory row must save correctly\"\"\"",
"        pred = PredictionHistory.objects.create(",
"            user=self.user,",
"            brand='Maruti',",
"            year=2020,",
"            km_driven=45000,",
"            fuel='Petrol',",
"            transmission='Manual',",
"            predicted_price=420000,",
"            lower_bound=378000,",
"            upper_bound=462000,",
"        )",
"        self.assertEqual(pred.brand, 'Maruti')",
"        self.assertEqual(pred.predicted_price, 420000)",
"        print('PASS: PredictionHistory saved correctly')",
"",
"    def test_prediction_belongs_to_user(self):",
"        \"\"\"History must only return records for that user\"\"\"",
"        PredictionHistory.objects.create(",
"            user=self.user, brand='Honda', year=2019,",
"            km_driven=60000, fuel='Diesel', transmission='Manual',",
"            predicted_price=550000, lower_bound=495000, upper_bound=605000",
"        )",
"        count = PredictionHistory.objects.filter(user=self.user).count()",
"        self.assertEqual(count, 1)",
"        print('PASS: History correctly filters by user')",
]));
C=C.concat(sp(1));

C.push(h2("6.1  How to Run the Django Tests"));
C.push(code([
"# In terminal (venv activated):",
"python manage.py test users",
"",
"# Expected output:",
"# Found 9 tests...",
"# PASS: UserProfile created with is_active=False",
"# PASS: User activation works",
"# PASS: Duplicate email correctly rejected",
"# PASS: Landing page loads (200)",
"# PASS: Login page loads (200)",
"# PASS: Register page loads (200)",
"# PASS: Dashboard redirects without login (302)",
"# PASS: Prediction redirects without login (302)",
"# PASS: Training redirects without login (302)",
"# PASS: Wrong password correctly rejected",
"# PASS: Correct login sets session",
"# PASS: PredictionHistory saved correctly",
"# PASS: History correctly filters by user",
"# Ran 9 tests in X.XXXs",
"# OK",
]));
C.push(pgB());

// ═══════════════════════════════════════════════════════
// SECTION 7 — FINAL CHECKLIST
// ═══════════════════════════════════════════════════════
C.push(secHdr(7,"Final Pre-Submission Checklist","Tick every box before submitting your project"));
C=C.concat(sp(1));

C.push(h2("7.1  UI Checklist"));
C.push(new Table({
  width:{size:9360,type:WidthType.DXA},columnWidths:[500,8860],
  rows:[
    ["Dark/Light toggle works on all pages"],
    ["All 12 screens load without 500 errors"],
    ["Login and logout work correctly"],
    ["Admin can activate users"],
    ["Training runs and saves charts"],
    ["Prediction form validates inputs"],
    ["Result page shows price + badge + similar cars"],
    ["History shows stat cards + delete works"],
    ["History detail has print button"],
    ["About page shows correct R\u00b2 from pkl file"],
    ["Compare cars returns winner + savings"],
    ["All dark mode colors are correct (no white text on white)"],
  ].map((r,i)=>new TableRow({children:[
    new TableCell({borders:BORD,width:{size:500,type:WidthType.DXA},shading:{fill:i%2===0?"FFFFFF":"F8FAFC",type:ShadingType.CLEAR},margins:{top:80,bottom:80,left:80,right:60},children:[new Paragraph({alignment:AlignmentType.CENTER,children:[new TextRun({text:"\u25A1",bold:true,size:22,font:"Arial",color:GREEN})]})]}),
    new TableCell({borders:BORD,width:{size:8860,type:WidthType.DXA},shading:{fill:i%2===0?"FFFFFF":"F8FAFC",type:ShadingType.CLEAR},margins:{top:80,bottom:80,left:120,right:100},children:[new Paragraph({children:[new TextRun({text:r[0],size:21,font:"Arial",color:GRAY})]})]}),
  ]}))
}));
C=C.concat(sp(1));

C.push(h2("7.2  ML Model Checklist"));
C.push(new Table({
  width:{size:9360,type:WidthType.DXA},columnWidths:[500,8860],
  rows:[
    ["python test_model.py — all 6 tests pass"],
    ["python test_metrics.py — all models above R\u00b2 0.70"],
    ["Best model R\u00b2 is above 0.85"],
    ["Newer car predicts higher price than older car"],
    ["Low KM car predicts higher price than high KM car"],
    ["Prediction is in reasonable range (not 0 or 999 crore)"],
    ["All 5 model pkl files exist in models/ folder"],
    ["Training page shows correct best model name"],
    ["About page shows correct R\u00b2 pulled from pkl"],
    ["python manage.py test users — all 9 tests pass"],
  ].map((r,i)=>new TableRow({children:[
    new TableCell({borders:BORD,width:{size:500,type:WidthType.DXA},shading:{fill:i%2===0?"FFFFFF":"F8FAFC",type:ShadingType.CLEAR},margins:{top:80,bottom:80,left:80,right:60},children:[new Paragraph({alignment:AlignmentType.CENTER,children:[new TextRun({text:"\u25A1",bold:true,size:22,font:"Arial",color:BLUE})]})]}),
    new TableCell({borders:BORD,width:{size:8860,type:WidthType.DXA},shading:{fill:i%2===0?"FFFFFF":"F8FAFC",type:ShadingType.CLEAR},margins:{top:80,bottom:80,left:120,right:100},children:[new Paragraph({children:[new TextRun({text:r[0],size:21,font:"Arial",color:GRAY})]})]}),
  ]}))
}));
C=C.concat(sp(2));

C.push(new Paragraph({alignment:AlignmentType.CENTER,children:[new TextRun({text:"\u2014  Testing Guide Complete  \u2014",size:22,font:"Arial",color:"9CA3AF",italics:true})],spacing:{before:260}}));

// BUILD
var doc=new Document({
  numbering:{config:[{reference:"bullets",levels:[{level:0,format:LevelFormat.BULLET,text:"\u2022",alignment:AlignmentType.LEFT,style:{paragraph:{indent:{left:720,hanging:360}}}}]}]},
  styles:{
    default:{document:{run:{font:"Arial",size:22}}},
    paragraphStyles:[
      {id:"Heading1",name:"Heading 1",basedOn:"Normal",next:"Normal",quickFormat:true,run:{size:38,bold:true,font:"Arial",color:NAVY},paragraph:{spacing:{before:280,after:130},outlineLevel:0}},
      {id:"Heading2",name:"Heading 2",basedOn:"Normal",next:"Normal",quickFormat:true,run:{size:28,bold:true,font:"Arial",color:BLUE},paragraph:{spacing:{before:200,after:80},outlineLevel:1}},
      {id:"Heading3",name:"Heading 3",basedOn:"Normal",next:"Normal",quickFormat:true,run:{size:24,bold:true,font:"Arial",color:GRAY},paragraph:{spacing:{before:160,after:60},outlineLevel:2}},
    ]
  },
  sections:[{
    properties:{page:{size:{width:12240,height:15840},margin:{top:1440,right:1000,bottom:1440,left:1000}}},
    children:C
  }]
});

Packer.toBuffer(doc).then(function(buf){
  fs.writeFileSync('/mnt/user-data/outputs/UsedCar_Testing_Guide.docx',buf);
  console.log('Done \u2014 '+buf.length+' bytes');
}).catch(function(e){console.error(e);process.exit(1);});
ENDJS