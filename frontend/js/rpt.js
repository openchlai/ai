
te["rpt_new_r"] = { div:[], c:
[
	{ div:["t15"], c:
	[ 
		{ s:["c w13 y","Name"] }, { txt:["c w25 gw ba","w25 x y","","usn","%7"] }, { div:["e"] } 
	]},

	{ div:["t15"], c:
	[
		{ s:["c w13 y","Group"] }, { txt:["c w25 gw ba","w25 x y","","fname","%15"] }, { div:["e"] }
	]},

	{ div:["t15"], c:
	[
		{ s:["c w13 y","Chart Type"] },
		{ div:["c w25 gw ba"], c:
		[
			{ div:["","va"], c:
			[
				{ txt:["c w21","w21 x y","","role_txt",":8::user_role:1"] }, 
				{ div:["d w03"], ac:["aa","","_dd","x y",""],  c:[ { div:["h02 w02 awb"] } ] },
				{ p:["e","o"], arg:["","role","%8"] }
			]},			
			{ div:["dd w25 ba gw cb","vdd"], ev:["_undd"], c:
			[
				{ uchk:["user_role_r","","user_role"] }
			]}
		]},
		{ div:["e"] }
	]},

	{ div:["t15"], c:
	[ 
		{ s:["c w13 y08 cb","X Axis:"] }, 
		{ div:["c","xaxis"], c:
		[
			{ p:["w34 t02","a"], u:["noop","noop"] },
			{ ac:["w15 ay t03","dsdsd-fld-xaxis-a","_nd","x y cb bd b","+ Add Group Field"] }
		]},
		{ div:["e"] } 
	]},

	{ div:["t15"], c:
	[ 
		{ s:["c w13 y08 cb","Y Axis:"] }, 
		{ div:["c","yaxis"], c:
		[
			{ p:["w34 t02","a"], u:["noop","noop"] },
			{ ac:["w15 ay t03","dsdsd-fld-yaxis-a","_nd","x y cb bd b","+ Add Group Field"] }
		]},
		{ div:["e"] } 
	]},

	{ div:["t15"], c:
	[ 
		{ s:["c w13 y08 cb","Metric:"] }, 
		{ div:["c","yaxis"], c:
		[
			{ p:["w34 t02","a"], u:["noop","noop"] },
			{ ac:["w10 ay t03","dsdsd-fld-yaxis-a","_nd","x y cb bd b","+ Add Metric"] }
		]},
		{ div:["e"] } 
	]},


	{ div:["t35 b05"], c:
	[
		{ div:["c w06 r02"], c:[ { ac:["ad btn","","_postj","x y w05 gbb bd ba_br cw tc","Save"] }, { s:["y07 bd b savl","..."] } ] },
		{ div:["c l20","va"], ac:["ay","","_vpcancel","x y w05 ba_br bd tc cbr","Cancel"], c:[ { p:["g","o"], arg:["",".id","%0"] } ] },
		{ div:["e"] }
	]}
]};

te["rpt_new"] = { vped:["w60 ma bd","New Call Report","call_rpt_new_r"] };

// ----------------------------------

te["rpt_ctx"] = { c:[ { arg:["","measure","%10"] }, { arg:["","g1","%12"] } ] };

te["rptvtt"] = { div:["d w11"], s:["x t b02 h02 tr b","%0"] };

te["rptvt"] = { div:["c w07 br"], s:["x t b02 h02 tr","%0"] };

te["rptv"] = { div:["c w07 br"], s:["x t b02 h02 tr","%0"] };

te["rptv_"] = { div:["c w07 br_br"], s:["x t b02 h02 tr","%0"] };

te["rptrt"] = { div:["b cb"], ev:["","","","","","_hilite","_uhilite"], c:
[ 
	{ div:["c w13"], s:["x08 t b02 h02 b","%0"] }, 
	{ div:["c bl"] },
	{ div:["e"] }
]};

te["rptrh"] = { div:["bb cb b"],  c:
[ 
	{ div:["c w13"], s:["x08 t b02 h02 b","%0"] }, 
	{ div:["c bl"] },
	{ div:["e"] }
]};

te["rptr_"] = { c:
[
	{ div:["ga",""], s:["bb_br",""], ev:["","","","","","_hilite","_uhilite"], c:
	[ 
		{ div:["c w13"], s:["x08 t b02 h02",null] }, 
		{ div:["c bl_br"] },
		{ div:["e"] }
	]},
	{ div:[] }
]};

te["rptra"] = { c: // "rpt","10","_g0","user_name", "context_masq_f"], 
[
	{ div:["","va"], s:["bb",""], ev:["","","","","","_hilite","_uhilite"], c:
	[
		{ div:["c w13"], ac:["aa","%10","_g","x08 t b02 h02 cbr",null], c:[ { arg:["","u","%11"] }, { arg:["","%12","%13"] }, { arg:["","%14","%1"] }, { p:["g","ctx"] }  ] },
		{ div:["c bl"] },
		{ div:["e"] }
	]},
	{ div:["g bt bb2 ga"] }
]};

te["rptr"] = { c:
[
	{ div:["",""], s:["bb",""], ev:["","","","","","_hilite","_uhilite"], c:
	[ 
		{ div:["c w13"], s:["x08 t b02 h02",null] }, 
		{ div:["c bl"] },
		{ div:["e"] }
	]},
	{ div:[] }
]};

te["rpt_xh_legend"] = { div:["col_v_x_l"], c: // 
[
	{ div:["","va"], ac:["","","_dd","%1",""], c:
	[
		{ div:["c t03 r05"], s:["w01 h01 gw","&nbsp;"], ucolor:["%2"] },
		{ div:["d"], s:["micon n cb g","show_chart"] }, 
		{ s:["","%0"] },
		{ div:["e"] }
	]},
	{ div:["dd w20 ba sh gw ml2","vdd"], c:
	[
		{ arg:["","","%3"] },
		//{ ac:["c","","_rpt_re","x y","Hide"] }
		{ input:["g","","rpt_r_hide","%3","checkbox"] },
		{ ac:["c w10 r ay","","_rpt_upd","xx y",""], c:
		[
			{ div:["c w01_ t"], s:["chk",""] },
			{ s:["c x y ","Hide"] },
			{ div:["e"] }			
		]},
		{ input:["g","","rpt_r_line","%3","checkbox"] },
		{ ac:["c w10 r ay","","_rpt_upd","xx y",""], c:
		[
			{ div:["c w01_ t"], s:["chk",""] },
			{ s:["c x y ","Line"] },
			{ div:["e"] }			
		]},		
	]}
]};

te["rpt_xh"] = { div:["col_v_x"], s:["%1","%0"] };

te["utable_hdr"] = { div:["col_h_y"], c:
[
        { s:["mlu1 mtu1 h02 x t gww",null] },
        { div:[""] }
]};

// ----------------------------------

te["_rpt_vw"] = { c:
[ 
	{ pivot:[] }, 
	{ div:["t20 b30"], c:[ { canvas:["","","",""], uchart:[] } ] },
	{ div:["ml"], utable:[] },
]}

te["rpt_vw"] = { _rpt_vw:["%4","%5"] };

// -------------------------------

te["rpt_dist_r"] = { div:["d w05 ba mln1"], c:
[
	{ input:["g","","yaxis","%0","radio","%9"] },
	{ li:["opta x y tc cb","","%1"], ev:["_rpt_opt"] }
]};

te["rpt_axis_tag"] = { li:["c w11 ba mr_","va"], s:["",""], c:
[
	{ s:["c w08 x y ",null] }, 
	{ input:["g","",null,"%0","checkbox","1"] },
	{ ac:["c w02 aa ","","_uchk_rpt","x w01 y","&Cross;"] },
	{ div:["e"] }
]};

te["rpt_axis_r"] = { div:[], c:
[
        { input:["g",null,"","%0","checkbox","%9"] },
        { ac:["r ay",null,"_chk_rpt","h02 x y cb",""], c:
        [
                { div:["c w01_ t"], s:["chk",""] },
                { s:["c x y ",null] },
                { div:["e"] }
        ]}
]};

te["rpt_hdr_menu_r"] = { div:[], c:
[
        { input:["g","",null,null,"radio",null] },
        { ac:["r ay","","_rpt_opt","xx y02 cb",""], c:
        [
                { div:["c w02 t"], s:["opt",""] },
                { s:["c w10 y07 ",null] },
                { div:["e"] }
        ]}
]};

te["rpt_hdr"] = { c: 
[
	{ ac:["c","","","x y07 n cb b",null] },
 	{ div:["d bd ll"], c:
        [
                { div:["mb_ ay","va"], ac:["","","_dd","x y gws",""], c:[ { s:["h2 cb micon","more_vert"] } ] }, // { img:["","","/helpline/images/more.png", "19"] }
                { div:["dd w15 x y mln13 ba gw sh","vdd"], ev:["_undd"], c:
                [
                        { rpt_hdr_menu_r:["xax","timeseries","1","XAxis Timeseries"] },
                        { rpt_hdr_menu_r:["xax","grouping","","XAxis Grouping"] },
                        { div:["mt b05 bt_"] },

                        { rpt_hdr_menu_r:["type","bar","1","Bar Chart"] },
                        { rpt_hdr_menu_r:["type","line","","Line Chart"] },
                        { div:["mt b05 bt_"] },

                        { input:["g","","stacked","stacked","checkbox","1"] },
                        { ac:["r ay","","_rpt_chk","xx y02 cb",""], c:
                        [
                                { div:["c w01_ t"], s:["chk",""] },
                                { s:["c x y ","Stacked"] },
                                { div:["e"] }
                        ]},
                        { div:["mt b05 bt_"] },

                        { rpt_hdr_menu_r:["valfn","0","1","Value"] },
                        { rpt_hdr_menu_r:["valfn","1","","Percentage"] },
                        { rpt_hdr_menu_r:["valfn","2","","Cummulative"] },
                        { rpt_hdr_menu_r:["valfn","3","","Cummulative Percentage"] },
                        { div:["mt b05 bt_"] },

                        { rpt_hdr_menu_r:["sortrpt","0","1","Sort By Name"] },
                        { rpt_hdr_menu_r:["sortrpt","1","","Sort By Total"] },
                ]}
        ]},
	{ div:["d"], s:["",""], c: // rpt_hdr:["Percent", "case_k_r","status","case_k", "case_k_tag","status", "-", "percent","%0"]  // ["Percent", "status", "status", "-", "percent", "0"]
        [
                { div:["d"], c: // xaxis
                [
                        { div:["ba","va"], s:["",""], c:
                        [
                                { div:["d w03"], ac:["ay","","_dd","x y04",""],  c:[ { div:["h02 w02 awb"] } ] },
                                { div:["e"] }
                        ]},
                        { div:["dd x y mln13 w15 gw ba mt1","vdd_rpt"], ev:["_undd"], c:[ { uchk:[null,null,null] } ] }
                ]},
                { div:["d"], uchk:[null,null] },
                { s:["d l20 r05 y07 cd","Y Axis:"] },
                { div:[] },
        ]},
        { div:["d"], s:["",""], c:
        [
                { uchk:["rpt_dist_r",null,null]}, // yaxis (distribution options)
                { s:["d l20 r05 y07 cd","X Axis:"] },
                { div:["e"] },
        ]},
        { div:["e"], c:
        [
                { input:["g","","rpt",null,"checkbox","1"] },
        ]}
]};

te["rpt_sum__"] = { li:[null], s:["xx yy w10",""], c:
[
	{ div:[], c:
	[
		{ div:["c t03 r05"], s:["w01 h01 gw","&nbsp;"], ucolor:[null] },
		{ s:["c",null] },
		{ div:["e"] }
	]},
	{ div:[], c:
	[
		{ s:["c t h b",null] },
		{ s:["c x t08 b",null] },
		{ div:["e"] }
	]}
]};

te["rpt_sum"] = { li:[null], s:["gw sh mr mb",""], c:
[
	{ div:["c w06 h06"], c:
	[
		{ ucolor:[null] },
		{ s:["micon h2 l20 t20 tc cw","call"] }
	]},
	{ div:["c w13"], c:
	[
		{ s:["xx tt tu",null] },
		{ div:[], c:
		[
			{ s:["c ll y b",null] },
			{ s:["c x y",null] },
			{ div:["e"] }
		]}
	]},
	{ div:["e"] }
]};

// -------------------------------

var COLOR = ["#3366cc","#3399FF", "#109618","#990099","#dc3912","#ff9900","#0099c6","#dd4477","#66aa00","#b82e2e","#316395","#994499","#22aa99","#aaaa11","#6633cc","#e67300","#8b0707","#651067","#329262","#5574a6", "#3b3eac","#b77322","#16d620","#b91383","#f4359e","#9c5935","#a9c413","#668d1c","#bea413","#0c5922","#743411"];

var CHARTS = {};

function rpt_val (j, r, r_, tot, a, m, fmt=1)
{
        var v = r[j][0]*1;
	var v_ = 0;
	var vtot = tot[j][0]*1;
	if (r_!=null) v_ = r_[j][0]*1;

        if (m[12]=="avg") 
	{
		v = ((r[j][1]*1)/(r[j][0]*1)); 
		vtot = ((tot[j][1]*1)/(tot[j][0]*1)); 
		if (r_!=null) v_ = ((r_[j][1]*1)/(r_[j][0]*1)); 
	}

	if (a[8]=="1") { v = (v*100) / (vtot*1); }	  // valfn=%
	if (a[8]=="2" ) { v = (v+v_); }			  // valfn=cumulative
	if (a[8]=="3" ) { v = ((v+v_)*100) / (vtot*1); }  // valfn=cumulative%

        v = (v*1).toFixed ((m[11]*1));

	if (fmt!=0) 
	{
		// todo: chart fmt eg seconds to hours
		return v;
	}

	var v_ = v;
	if (m[7].length>0) v_ = valf ([v], m[7]);
	if (a[8]=="1" || a[8]=="3") v_ = v+"%";
        return v_;
}

// ----------------------------------------------------------------

function rpt_download_text (p)
{
	var a = {}
	argv (p.previousSibling, a);
	console.log (" [rpt-args] "+JSON.stringify (a))

	var v = "";
	var f = 0;
	var i_ = 0;
	var j_ = 0;


	XLSX.xlsx_sheet_start ("TITLE");

	var coll = p.childNodes[1].childNodes;
	for (var i=0; i<coll.length; i++) 
	{
		i_ = ((i*1)+3);
		XLSX.xlsx_row_start (i_);
		var coll_ = coll[i].childNodes;
		for (var j=0; j<coll_.length; j++)
		{
			j_ = j+1;
			f = 0;
			v = "";	
			if (coll_[j].className=="e") f=1; 
			if (coll_[j].className=="col_h_y") { f=1; v=coll_[j].childNodes[0].innerHTML; } // todo: multiple y axis
			if (coll_[j].className=="col_v_x_l") { f=1; v=coll_[j].firstChild.firstChild.firstChild.childNodes[2].innerHTML; }
			if (f==0) { v=coll_[j].firstChild.innerHTML; }
			if (v=="&nbsp;") v="";
			// console.log ("("+i_+","+ j+") "+coll_[j].className+"="+v)
			XLSX.xlsx_cell (i_, j_, v);
		}
		XLSX.xlsx_row_end ();
	}
	XLSX.xlsx_sheet_end ();
	XLSX.xlsx_file (p.childNodes[0], (a.yaxis=="-"));
	
	console.log (XLSX.fz.b)
	console.log ("fz len: "+XLSX.fz.i +","+ XLSX.fz.j +","+ XLSX.fz.n)
	
	XLSX.fb.rst().append ("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
	console.log ("CRC: "+XLSX.xlsx_crc32 ())
	
	const fa = new Uint8Array (XLSX.fz.n);
	var i = 0, l=0;
	for (var n=0; n<XLSX.fz.n; n+=1024)
	{
		l = XLSX.fz.n-n;
		if (l>1024) l=1024;
		fa.set (XLSX.fz.b[i].subarray (0,l), n)
		i++;
	}
	
	const blob = new Blob ([fa.buffer], {type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"});
	const blobURL = window.URL.createObjectURL (blob);
	const tempLink = document.createElement('a');
	tempLink.style.display = 'none';
	tempLink.href = blobURL;
	tempLink.setAttribute('download', "Report.xlsx");
	//// Safari thinks _blank anchor are pop ups. We only want to set _blank
	//// target if the browser does not support the HTML5 download attribute.
	//// This allows you to download files in desktop safari if pop up blocking
	//// is enabled.
  
	document.body.appendChild(tempLink);
	tempLink.click();
	document.body.removeChild(tempLink);
	setTimeout(() => {
    	//	// For Firefox it is necessary to delay revoking the ObjectURL
    		window.URL.revokeObjectURL(blobURL);
  	}, 100);

}

function rpt_download (p) // upload image first then text
{
	XLSX.fz.rst ();
	XLSX.cdrec.rst ();
	XLSX.fb.rst();
	
	var img = p.getElementsByTagName ("canvas"); //console.log (img);
	
	img[0].toBlob (function (blob)
	{
		var reader = blob.stream ().getReader ();
		reader.read().then (function onread ({done, value}) 
		{
			if (done) 
			{
				console.log ("PROMISE DONE!!!!")
				XLSX.xlsx_file_sub ("xl/media/image1.png");
				rpt_download_text (p);
				return; 
			}
			XLSX.fb.set (value)
			return reader.read ().then (onread);
		}); 
	}, "image/png", 1);
}

// ----------------------------------------------------------------

function uchart_vw (el, lbl, ds, cht, stacked)
{     
	var wi = 35;
	if (stacked==false && cht=="bar" && ds.length>0) wi = 10*ds.length;
	var wn = Math.floor ((screen.width - 100)/wi); 
	if ((cht=="bar" || cht=="line") && lbl.length<wn)
	{
		for (var i=lbl.length; i<wn; i++) lbl[i]=".";
	}

	var co = { type:cht, scaleLineColor:"rgba(255,255,255,0)" };
	if (cht=="pie")
	{
		co.type="doughnut";
		co.options = { legend: { display:false } }; 
	}
	else
	{
		co.options = { scales:  // c5cad3
		{ 
			xAxes:[ { gridLines: { display:false, drawTicks:false, lineWidth:0, color:"rgba(0,0,220,1)", drawBorder:true }, stacked:false, ticks:{ padding:8 }, /*scaleLabel: { display: true, labelString: 'probability' }*/ } ],
			yAxes:[ { gridLines: { display:true,  drawTicks:false, lineWidth:1, color:"rgba(197, 193, 211, 0.5)", drawBorder:false }, stacked:false, ticks:{ "min":0 } } ]
		}, legend: { display:false } }; 

		// if (yn<1) co.options.legend.display = false;
		if (stacked) {  co.options.scales.xAxes[0].stacked=true; co.options.scales.yAxes[0].stacked=true; }
	}
	co.data = { labels:lbl, datasets:ds };	
	//co.options.responsive = true;
	co.options.maintainAspectRatio = false;
	
	//console.log ("chart-------------------")
	//console.log (co);
	
	const bg_plugin = 
	{
		id: 'custom_canvas_background_color',
		beforeDraw: (chart) => 
		{
			const ctx = chart.canvas.getContext('2d');
			ctx.save();
			ctx.globalCompositeOperation = 'destination-over';
			ctx.fillStyle = '#ebedf0';
			ctx.fillRect(0, 0, chart.width, chart.height);
    			ctx.restore();
  		}
	};
	co.plugins = [bg_plugin]
	
	var ctx = el.getContext ('2d');
	var chart1 = new Chart (ctx, co);
}

function uchart (el, _u, _a, _r, _m)
{
	var xx = ra[(_r[0]+"_x")];
	var yy = ra[(_r[0]+"_y")];
	var zz = ra[(_r[0]+"_z")];
	var rr_ = ra[(_r[0]+"_pivot")];
	var tot = ra[(_r[0]+"_tot")];
	var fmt = ra[(_r[0]+"_fmt")];
	var yyn = ra[(_r[0]+"_yyn")];
	var ct = ra[(_r[0]+"_ct")];
	var rrxi_ = ra[(_r[0]+"_rrxi")];
	var rryi_ = ra[(_r[0]+"_rryi")];
	var color_ = ra[(_r[0]+"_color")];
	var xn = xx.length;
	var yn = yy.length;
	var zn = Object.keys(zz).length;
	var n = (1*xn)+(1*yn);	
	var chart_type = _r[5];
	var stacked = _r[6].length>0;
	var mm = re["metrics"][_r[4]];
	var i = 0;
	var j = 0;
	var k = 0;
	var l = 0;
	var c = 0;
	var m = 0;
	var z = 0;
	var jn = tot.length-2;
	//if (yn==0) jn = tot.length-1;
	var _i = 0;
	var i_ = 0;
	var j_ = 0;
	var r = null;
	var r_ = null;
	var lv = null;
	var v = null;
	var v_ = null;
	var rs = null;

	var lbl = [];
	var ds = [];

	for (j=xn; j<tot.length-2; j++) // x axis labels
	{
		if (ct[j][0]==0) continue; // skip blank columns
		v = "";
		j_ = (j-xn);
		for (k=0; k<yn; k++) 
		{
			m = yyn[yn-1-k];
			if (k==yn-1) m = yy[k].length; 
			// console.log (" m:"+m+" yn:"+yn+" k:"+k+" | "+ yyn[yn-1-k] +" | "+j_+" ("+j+")")

			c = Math.floor(j_/m);
			j_ = j_%m; 
			if (k==yn-1) c = j_;

			if (k>0) v+="/"; 
			var v_ = yy[k][c];
			var fmti = (k*1)+(xn*1)
			if (fmt[fmti].length>0) v_ = valf ([v_], fmt[fmti]);
			if (v_.length<1) v_ = "(blank)" 
			v += v_;
		}
		lbl[l] = v;
		l++;
	}

	// console.log ("[xaxis labels] "+(tot.length-xn-xn)+" "+JSON.stringify (lbl))

	var rn = tot.length-xn-2;
	var h = 200; 
	var w = (rn*25)+100;
	if (stacked==false) w = (rr_.length*rn*1)+100;
	// console.log ("[chart_size] "+h+","+w+" | "+screen.width);
	if (w<(screen.width-100)) w = screen.width - 100; 
	
	for (i=0; i<rr_.length; i++) // generate dataset
	{
		_i = i_;
		i_ = i;
		if (xn>0 && rrxi_) i_ = rrxi_[i]; // sort by xaxis-name (default)
		if (_r[7]=="1") // sort by xaxis-tot
		{
			i_ = rryi_[i].i
		}
		// console.log ( "  rr_:"+i+" / "+i_)
		r_ = rr_[i_];
		if (!r_) continue;
				
		v = "";
		//if (mn>1 && zn>1) v ="("+zz[z][6]+") "; // prefix label
		for (j=0; j<xn; j++) 
		{ 
			if (j>0) v+="/"; 
			var v_ = r_[j][0]; 
                        if (fmt[j].length>0) v_ = valf ([v_], fmt[j]);
                        if (v_.length<1) v_ = "(blank)"
                        v += v_;
		}
		lv = v;
		
		v = ""
	 	rs = [];
		j_ = 0;
		for (j=xn; j<jn; j++)
		{
			v = rpt_val (j, r_, null, tot, _r, mm);
			rs[(j-xn)] = v;
			// for (k=0; k<zn; k++) // accumulate after r_ -- not applciable here  - will messup chart
                        //{
                        //        ar[j][k] += r_[j][k]*1;
                        //        // console.log (" > acc "+i+" "+j+" "+k+" | "+r_[j][k]);
                        //}
		}
			
		l = ds.length;
		ds[l] = { label:lv, lineTension:0.1, borderColor:color_[i_], backgroundColor:"#FFFFFF00", barPercentage:0.5, order:2, data:rs };
		if (_r[5]!="line" || yn<1) ds[l].backgroundColor = color_[i_];
		// if (u[1]=="line" && yn>0) ds[l].borderWidth = 2.0;
		// if (lv=="Abandoned" && yn>0) { ds[l].type = "line"; ds[l].backgroundColor="#FFFFFF00"; }
		
		// console.log (i+": "+color_);
	}
	
	if (xn>0 && yn==0) 
	{ 
		// console.log ( "[lbl] "+ JSON.stringify (lbl))
		// console.log ( "[ds] "+JSON.stringify (ds))
		chart_type = "pie"; 
		stacked=false; 
		w=200; 
		lbl_=[]; 
		ds_= [{ data: [], backgroundColor:[] }];
		for (var i=0; i<ds.length; i++)
		{
			lbl_[i] = ds[i].label;
			ds_[0].data[i] = ds[i].data[0];
			ds_[0].backgroundColor[i] = ds[i].backgroundColor;
		}
		//console.log (" [lbl_] "+JSON.stringify (lbl_))
		//console.log (" [ds_] "+JSON.stringify (ds_))
		lbl = lbl_;
		ds = ds_;
	}

	CHARTS[__(el).id] = { "ds":ds, "lbl":lbl, "type":chart_type, "stacked":stacked, "h":h, "w":w };

	el.height = h; 
	el.width = w;
	
	uchart_vw (el, lbl, ds, chart_type, stacked, h, w);
}

// ----------------------------------------------------------------

function table_hdr_metric (el,zz,z)
{
	for (var k=0; k<mm_.length; k++) // todo: multi-column metric
	{
		z = mm_[k];
		nd (el, te["s"], [zz[z][6],"c w08 x t h02 br bt"], [], [2]);		
	}
	nd (el, te["s"], ["","e"], [], [2]);
}

function table_hdr (el, xn, y, yy, fmt)
{
	var el_ = null;
	var v ="";
	var cn ="";
	var yn = yy.length;
	for (var j=0; j<yy[y].length; j++) 
	{
		v = yy[y][j];
		var fmti = (y*1)+(xn*1);
		if (fmt[fmti].length>0) v = valf ([v], fmt[fmti]);
		if (v.length<1) v = "(blank)";
		el_ = nd (el, te["utable_hdr"], [v], [], [1]); 
		if (y<yn-1) 
		{
			// el_.style.marginTop = "1px";
			table_hdr (el_, xn, y+1, yy, fmt);
			nd (el_, te["s"], ["","e"], [], [2]);
		}
		if (y==yn-1)
		{
			el_.previousSibling.style.width = "80px";
		}
	}
}
 
function utable (el, _u, _a, _r, _m)
{
	var xx = ra[(_r[0]+"_x")];
	var yy = ra[(_r[0]+"_y")];
	var zz = ra[(_r[0]+"_z")];
	var rr_ = ra[(_r[0]+"_pivot")];
	var tot = ra[(_r[0]+"_tot")];
	var fmt = ra[(_r[0]+"_fmt")];
	var yyn = ra[(_r[0]+"_yyn")];
	var ct = ra[(_r[0]+"_ct")];
	var rrxi_ = ra[(_r[0]+"_rrxi")];
	var rryi_ = ra[(_r[0]+"_rryi")];
	var color_ = ra[(_r[0]+"_color")];
	var xn = xx.length;
	var yn = yy.length;
	var zn = Object.keys(zz).length;
	var n = (1*xn)+(1*yn);	
	var chart_type = _r[5];
	var stacked = _r[6].length>0; 
	var mm = re["metrics"][_r[4]];
	var i = 0;
	var j = 0;
	var k = 0;
	var l = 0;
	var c = 0;
	var m = 0;
	var z = 0;

	var i_ = 0;
	var k_ = 0;
	var _i = -1;
	var jn = tot.length-1;
	if (xn>0 && yn==0) jn = tot.length-2;
	var r = null;
	
	var w = ((xn*161)+(yyn[yn]*91)+(122));
	el.style.width = w+"px";

	var ar = [];
	var ys = xn+(yyn[yn]) + 1; // total column count
	if (yn==0) ys++;
	for (j=0; j<=ys; j++) // init totals
	{ 
		ar[j]=[];  
		for (k=0; k<zn; k++) ar[j][k]=0; 
	}

 	// console.log ("UTABLE: xn:"+xn+" wy:"+wy+" zn:"+zn+" w:"+w+" | yy.length="+yy.length+" "+JSON.stringify (yy))

	// header -----------------------------------
	var el_ = nd (el, te["l"], ["gwg"], [], [1]); 
	var el__ = null;
	for (j=0; j<xn; j++)
	{
		el__ = nd (el_, te["s"], ["","col_h_x"], [], [2])
		nd (el__, te["s"], ["&nbsp;","xx t h02 gww"], [], [2]);
		for (var j_=1; j_<yy.length; j_++) nd (el__, te["s"], ["&nbsp;","xx t06 h02 gww "], [], [2]); 	// y axis hdr label
	}
	if (yy.length>0)
	{
		table_hdr (el_, xn, 0, yy, fmt); // mm, fmt, tot);
	}
	v = "Total";
	if (m[8]=="avg") v = "Average";	
	el__ = nd (el_, te["s"], ["","col_h_tot"], [], [2]);
	nd (el__, te["s"], [v,"xx t h02 tr gww"], [], [2]); 
	for (var j_=1; j_<yy.length; j_++) nd (el__, te["s"], ["&nbsp;","xx t06 h02 gww "], [], [2]); 
	nd (el_, te["s"], ["","e"], [], [2]);
	
	// data -----------------------------------
	for (i=0; i<rr_.length; i++)
	{
		_i = i_;
		i_ = i;
		if (xn>0 && rrxi_) i_ = rrxi_[i]; // sort by xaxis name
		if (_r[7]=="1") i_ = rryi_[i].i; // sort by xaxis total

		// console.log ( "  rr_:"+i+"of"+rr_.length+" | "+i_)
		r_ = rr_[i_];
		if (!r_) continue;
		
		el_ = nd (el, te["l"], ["gwg"], [], [1]); // new row
//		el_.style.width = w+"px";
	
		for (j=0; j<xn; j++) 	// xaxis headers
		{
			var v_ = r_[j][0]; 
                        if (fmt[j].length>0) v_ = valf ([v_], fmt[j]);
                        if (v_.length<1) v_ = "(blank)"
			// console.log ("x("+j+") "+ v_)
			cn = "xx t h02 mtu1 gw cb";
			if (i>0 && r_[j][0]==rr_[_i][j][0]) 
			{
				if (j==0 || (j>0 && r_[j-1][0]==rr_[_i][j-1][0]))
				{
					cn="xx t06 h02 gw cb"; 
					v_=""; 
				}
			}
			var tp = "rpt_xh";
			if (j==xn-1) { tp = "rpt_xh_legend"; }
			el__ = nd (el_, te[tp], [], [v_, cn, color_[i_], ""], [0]); 
		}

		for (j=xn; j<jn; j++)	// data
		{
			cn = "col_v_y";
			if (j==jn-1) { cn = "col_v_tot"; };
			el__ = nd (el_, te["s"], ["",cn], [], [2]); 
			// for (k=0; k<zn; k++) // todo: multi-column metrics
			{
				v = rpt_val (j, r_, null, tot, _r, mm);
				elv = nd (el__, te["s"], [v,"xx t h02 tr"], [], [2]); 
			}
			for (k=0; k<zn; k++) // accumulate after r_
                        {
                                ar[j][k] += r_[j][k]*1;
                                // console.log (" > acc "+i+" "+j+" "+k+" | "+r_[j][k]);
                        }
		}
	
		nd (el_, te["s"], ["","e"], [], [2]); 
	}
	
	// footer -----------------------------------	
	el_ = nd (el, te["l"], ["gwg bb"], [], [1]); 
	
	for (j=0; j<xn; j++)  
	{
		v = "";
		if (j==xn-1) 
		{
			v = "Total";
			if (m[8]=="avg") v = "Average";	
		}
		el__ = nd (el_, te["s"], ["","col_f_x"], [], [2]); 
		nd (el__, te["s"], [v,"xx t h02"], [], [2]);
	}
		
	for (j=xn; j<jn; j++)	// data
	{
		cn = "col_f_y";
		if (j==jn-1) cn = "col_f_tot"; 
		el__ = nd (el_, te["s"], ["",cn], [], [2]); 
		// for (k=0; k<zn; k++) // todo: multi-column metrics
		{
			v = rpt_val (j, tot, null, tot, _r, mm);
			nd (el__, te["s"], [v,"xx t h02 tr"], [], [2]); 
		}
	}
	nd (el_, te["s"], ["","e"], [], [2]); 
		
	return el;
}	

// ----------------------------------------------------------------

function usummary (el, _u, _a, _r, _m)
{
	 var xx = ra[(_r[0]+"_x")];
        var yy = ra[(_r[0]+"_y")];
        var zz = ra[(_r[0]+"_z")];
        var rr_ = ra[(_r[0]+"_pivot")];
        var tot = ra[(_r[0]+"_tot")];
        var fmt = ra[(_r[0]+"_fmt")];
        var color_ = ra[(_r[0]+"_color")];
        var rrxi_ = ra[(_r[0]+"_rrxi")];
        var i = 0;
        var i_ = 0;
        var xn = xx.length;
        var jn = tot.length-2;
        var zn = Object.keys(zz).length;
        var m = re["metrics"][_r[4]];
        var r_ = null;
        var lbl = null;
        var v = null;

        for (i=0; i<rr_.length; i++)
        {
                if (xn<1) break;
                i_=i;
                if (xn>0 && rrxi_) i_ = rrxi_[i]; // sort by xaxis name
                if (_r[7]=="1") i_ = rryi_[i].i; // sort by xaxis total
                r_ = rr_[i_]

                lbl = "";
                for (j=0; j<xn; j++)
                {
                        if (j>0) lbl+="/";
                        var lbl_ = r_[0][0];
                        if (fmt[j].length>0) lbl_ = valf ([lbl_], fmt[j]);
                        lbl += lbl_;
                }
                v = rpt_val (jn, r_, null, tot, _r, m);
                nd (el, te["rpt_sum"], [m[10], v, lbl, color_[i_], "c mr mb "], [], [5]);
        }

        lbl = "Total";
        if (m[12]=="avg") lbl = "Average";
        v = rpt_val (jn, tot, null, tot, _r, m);
        nd (el, te["rpt_sum"], [m[10], v, lbl,"#0073b7","c mr mb"], [], [5]);
        nd (el, te["s"], ["","e"], [], [2]);
}

// ----------------------------------------------------------------

function pivot_sort_list_y (u, rr_, n) // sorting by right total
{
	var k = [];
	for (var i=0; i<rr_.length; i++)
	{
		// console.log ("[y] "+JSON.stringify (rr_))
		k[i] = { "i":i , "k":rr_[i][0][0], "v":rr_[i][n][0]*1 }
	}
	var k_ = k.sort ( function (a,b){ if (a.v==b.v) return 0; return a.v>b.v?-1:1; } );
	ra[(u+"_rryi")] = k_;
}

function pivot_sort_list_x (u, xx, rrx, fmt)
{
	 var ri = [];
        var i = 0;
        var _i=-1;
        var j = [];
        var rx = [];
        var xn = xx.length;
        var c = 0;
        var v = 0;

        // console.log ("rrx("+u+")-------------------------")
        // console.log (rrx)

        for (i=0; i<=xn; i++) j[i]=[0,0];
        rx[0] = rrx;
        i=0;
        while (i>-1)
        {
                if (i>0 && rx[_i].k[j[_i][0]]!=undefined)
                {
                        var rk_ = null; // rk[xx[_i]];

			if (fmt[_i].length>0)
			{
				var vv = fmt[_i].split (":");
				if (vv[1].length==0 && vv[2].length>1) rk_ = rk[vv[2]];
			}

                        if (rk_!=null) // sork by rk
                        {
                                for (j[_i][1]; j[_i][1]<rk_.length; j[_i][1]++) // skip missing val
                                {
                                        rx[i] = rx[_i].c[ rk_[j[_i][1]] ];
                                        if (rx[i]!=undefined) { j[_i][1]++; break; }
                                }
                        }

			if (i==xn) // update index
                        {
                                ri[ri.length] = rx[i].a
                        }
                }

                if  (rx[i] && rx[i].k.length>0) // descend
                {
                        _i=i;
                        i++;
                        j[i][0]=0;
                        j[i][1]=0;
                        rx[i] = rx[_i].c[ rx[_i].k[ j[_i][0] ] ];
                        continue;
                }

                if (_i>-1)  // list
                {
                        j[_i][0]++;
                        if (j[_i][0]<rx[_i].k.length) // next sibling
                        {
                                rx[i] = rx[_i].c[ rx[_i].k[j[_i][0]] ];
                                continue;
                        }
                }

                i--;
                _i=i-1; // ascend
                if (i>0)
                {
                        j[_i][0]++;
                        rx[i] = rx[_i].c[ rx[_i].k[j[_i][0]] ];
                        j[i][0]=0;
                        j[i][1]=0;
                        continue;
                }

                break;
        }

        ra[(u+"_rrxi")] = ri;
       // console.log ("rrxi("+u+")"+ JSON.stringify (ri))
}

function pivot_close_row (xn, ynn, zn, j_, r_, tot, xtot)
{
	var j=0, z=0, c=0;
	var htot = [];
	var hc = [];
	for (z=0; z<zn; z++) { htot[z]=0; hc[z]=0; }

	for (j=j_; j<ynn; j++) // fill blanks
	{ 
		c = (1*xn)+(1*j);
		r_[c]=[]; 
		for (z=0; z<zn; z++) r_[c][z]=""; 
	}

	for (j=xn; j<r_.length; j++) 
	{
		for (z=0; z<zn; z++) if (r_[j][z].length>0) { htot[z] += (1*r_[j][z]); hc[z]++; }
	}

	j=r_.length; 
	r_[j]=[];
	for (z=0; z<zn; z++) { r_[j][z] = (""+htot[z]); tot[j][z]+=htot[z]; }
	j++;
	r_[j]=[];
	for (z=0; z<zn; z++) { r_[j][z] = (""+hc[z]); tot[j][z]+=hc[z]; }

	if (xtot)
	{
		r_[(j-1)][0] = xtot[r_[0]];
		// console.log ("[xtot] "+r_[0]+":"+xtot[r_[0]]+" | "+JSON.stringify (xtot))
	}
}

function pivot (el, _u, _a, _r, _m)
{
	var xx = ra[(_r[0]+"_x")];
	var yy = ra[(_r[0]+"_y")];
	var zz = ra[(_r[0]+"_z")];
	var rr = ra[_r[0]];
	var i = 0;
	var i_ = 0;
	var j = 0;	
	var j_ = 0;
	var j__ = 0;
	var z = 0;
	var k = 0;
	var g = -1;
	var xn = xx.length;
	var yn = yy.length;
	var zn = Object.keys(zz).length;
	var n = (1*xn)+(1*yn);
	var v = "";
	var x = 0;
	var y = 0;
	var y_ = 0;
	var r = null;
	var r_ = null;
	var rr_ = [];
	var gx = [];
	var gy = [];
	var rrx = { a:0, b:0, c:{}, k:[] };  // build an index tree of x then flatten to rrxi
	var tot = [];
	var ct = [];
	var xtot = null;
	if (xn>0) xtot = ra[(_r[0]+"_xtot")];
	var gtot = ra[(_r[0]+"_gtot")];
	
	var fmt = ra[(_r[0]+"_fmt")];
	var COLOR_ = [51,102,188]; // 0x3366cc;	// start color (shade of blue)
	var color_ = [];
	var color__ = "";

	// var el_ = __(el,"rpt")
	var a = { }
	argv (el.previousSibling, a);
	_r[4] = a.rpt;	
	_r[5] = a.type;	
	_r[6] = a.stacked && a.stacked.length>0?"1":"";	
	_r[7] = a.sortrpt;
	_r[8] = a.valfn; // v, cu, percent, pcu 

	var yyn = [0];
	if (yn>1) yyn[1] = yy[(yn-2)].length; 
	for (j=2; j<yn; j++) yyn[j] = yy[(yn-j-1)].length * yyn[(j-1)];
	if (yn>0) yyn[yn] = yy[yn-1].length
	if (yn>1) yyn[yn] = yyn[yn-1] * yy[yn-1].length;

	var ys = xn+(yyn[yn]) + 1; // total column count
	if (yn==0) ys++;
	for (j=0; j<=ys; j++) // init totals
	{ 
		tot[j]=[]; 
		ct[j]=[]; 
		for (k=0; k<zn; k++) { tot[j][k]=0; ct[j][k]=0; } 
	}
		
	for (i=0; i<rr.length; i++)
	{
		r = rr[i];
		
		g = -1;

		for (j=0; j<xn; j++) if (r[j]!=gx[j]) // change in x-axis
		{
			g=j; 
			gx[j]=r[j];
			for (k=g+1; k<xn; k++) gx[k]=r[k];
			break; 
		}
		
		if (i==0 && xn==0) g=0; // default row if no xaxis defined

		if (g>-1) // new row
		{
			if (i>0) // close previous row
			{
				pivot_close_row (xn, yyn[yn], zn, j_, r_, tot, xtot);
			}
			
			i_ = rr_.length;
			rr_[i_] = []; // new row
			r_ = rr_[i_];
			for (j=0; j<xn; j++) r_[j] = [r[j]]; // xaxis
			j_=0;

			var rx_ = rrx; // update index
			for (j=0; j<xn; j++) 
			{
				if (rx_.c[r_[j]]==undefined) 
				{
					rx_.c[r_[j]] = { a:i_, b:i_, c:{}, k:[] };
					rx_.k[rx_.k.length] = r_[j][0];
				}
				else rx_.c[r_[j]].b = i_;
				rx_ = rx_.c[r_[j]];
			}

			color__ = "rgb("+COLOR_[0]+","+COLOR_[1]+","+COLOR_[2]+")";
			if (xn==1 && fmt[0].length>1) color__ = ve ([r[0]], ["","",fmt[0].split (":")[2],"0","5"]); 
			color_.push (color__); 
			for (var j=0; j<3; j++) 
			{ 
				COLOR_[j] = COLOR_[j]+21+(21*j);
				if (COLOR_[j]>255) COLOR_[j]=COLOR_[j]%255; 
			}
				
		}
		
		for (j=0; j<yn; j++) gy[j]=-1;
		for (j=0; j<yn; j++) // match yaxis to yset
		{
			y_ = (1*xn)+(1*j);
			for (k=0; k<yy[j].length; k++)
			{
				if (yy[j][k]==r[y_]) 
				{ 
					gy[j] = k;
					break; 
				}
			}
			if (gy[j]<0) { console.log ("pivot error: no match on yaxis for r:"+i+" j:"+y_+" r[j]"+r[y_]); break; }
		}
		if (yn>0 && j<yn && gy[j]<0) { console.error ("pivot error: no match for full yaxis"); continue; } // skip row if yaxis failed to match

		j__ = 0;
		for (k=0; k<yn-1; k++) { j__ += (gy[k]*yyn[(yn-1-k)]); }
		if (yn>0) j__ += gy[(yn-1)];
		for (j=j_; j<j__; j++) 
		{ 
			r_[(j+xn)]=[]; 
			for (z=0; z<zn; z++) r_[(j+xn)][z]="";  // fill blanks
		}

		r_[(j__+xn)] = [];
		for (z=0; z<zn; z++) 
		{
			r_[(j__+xn)][z] = r[n+z];
			tot[(j__+xn)][z] += (r[n+z]*1)
			ct[(j__+xn)][z]++;
		}
		j_ = j__;
		j_++ 
	}

	if (i>0) // close last row
	{
		pivot_close_row (xn, yyn[yn], zn, j_, r_, tot, xtot);
		if (gtot!==undefined) tot[(xn+yyn[yn])][0] = gtot;
	}

	pivot_sort_list_x (_r[0], xx, rrx, fmt);
	
	pivot_sort_list_y (_r[0], rr_, tot.length-2);

	ra[(_r[0]+"_pivot")] = rr_;
	ra[(_r[0]+"_yyn")] = yyn;
	ra[(_r[0]+"_tot")] = tot;
	ra[(_r[0]+"_ct")] = ct;
	ra[(_r[0]+"_color")] = color_;

	// console.log ("pivot-----------xn:"+xn+"  rows:"+rr_.length+" cols:"+yn+","+ys+","+JSON.stringify (yyn)+ " | "+JSON.stringify (tot));
	// console.log (rr_);
	// console.log (color_)
	
	return el;
}

function rpt (el)
{
	var u_ = el.id.split ("-");
	var a = {"args":"?"};
	var pm = __(el,"vftab").childNodes[1];
	argv (pm, a, "name");		// get filters
	argv (el.previousSibling, a);	// get rpt args 
	// console.log ("rpt=>"+JSON.stringify (a))
	var m = re["metrics"][a.rpt];
	if (m[4].length>0) u_[1]=m[4];
	if (m[5].length>0 && !a.xaxis) a.args += "xaxis="+m[5]+"&";
	if (m[6].length>0) a.args += "metrics="+m[6]+"&"
	if (a.distf) a.args += "yaxis="+re["distf"][a.distf][2]+"&";
	url (el, u_[0], u_[1], a.args, null, 0);
}

// ----------------------------------------------------------------------
 
function _uchk_rpt (ev)
{
	var k = this.previousSibling.name;
	var v = this.previousSibling.value;
	var el = __(this);
	var p = el.parentNode;
	var coll = p.previousSibling.childNodes[1].getElementsByTagName ("input");
	for (var i=0; i<coll.length; i++) // find tag
	{
		if (coll[i].id==k && coll[i].value==v) 
		{ 
			coll[i].checked = false; 
			break; 
		}
	}
	var pv = __(this,"vrpt");
	p.removeChild (el);

// console.log ("  id::"+pv.id);
	rpt (pv.nextSibling);

	boo (ev)
}

function _chk_rpt ()
{
	var k = this.previousSibling.id;
	var v = this.previousSibling.value;
	var b = chk (this.previousSibling);
	var p = __(this).parentNode.nextSibling;
	var el = null;
	var coll = p.getElementsByTagName ("input");
	for (var i=0; i<coll.length; i++) // find tag
	{
		if (coll[i].name==k && coll[i].value==v) { el=coll[i]; break; }
	}
	if (b==false) // remove tag
	{
		if (el==null) return;
		el = __(el);
		p.removeChild (el);
		return;
	}
	if (el!=null) return;
	nd (p, te[this.id], [], [v], [0]);	
}

function _rpt_chk ()
{
	var b = chk (this.previousSibling);
	rpt (__(this,"vrpt").nextSibling);
}	

function _rpt_opt ()
{
	this.previousSibling.checked = true;
	rpt (__(this,"vrpt").nextSibling);
}

function _rpt ()
{
	
	rpt (__(this,"vrpt").nextSibling);
}

function _rpt_upd () // re-render chart
{
	var b = __(this);
	var p = __(b,"vt");
	var el = p.childNodes[1].firstChild;
	var co = CHARTS[p.id];
	var lbl = b.firstChild.value;
	var v = chk (this.previousSibling)
	var a = { hiderow:"", showingline:"g" }
	argv (b, a);
	
	if (a.rpt_r_hide!=undefined) a.hiderow = "cancel"
	if (a.rpt_r_line!=undefined) a.showingline = "";
	b.previousSibling.firstChild.firstChild.childNodes[2].className = a.hiderow;
	b.previousSibling.firstChild.firstChild.childNodes[1].firstChild.className = a.showingline;
	
	el.innerHTML = "";
	var el_ = document.createElementNS ("http://www.w3.org/1999/xhtml", "canvas");
	el_.className="";
	el_.id="";
	el_.width=co.w;
	el_.height=co.h;
	el.appendChild (el_);
	
	var ds_ = [];
	var lbl_ = co.lbl;
	var ds__ = [];
	var i_ = -1;
	var LL = { true:["",""], false:["",""] }
	
	if (co.type=="pie")
	{
		ds_= [{ data: [], backgroundColor:[] }];
	 	lbl_ = [];
		for (var i=0; i<co.lbl.length; i++)
		{
			if (co.rpt_r_hide==undefined) { co.rpt_r_hide=[]; co.rpt_r_line=[]; }
			if (co.lbl[i]==lbl) co[this.previousSibling.name][i] = v;
			if (co.rpt_r_hide[i]==true) continue;
			i_ = lbl_.length;
			lbl_[i_] = co.lbl[i];
			ds_[0].data[i_] = co.ds[0].data[i];
			ds_[0].backgroundColor[i_] = co.ds[0].backgroundColor[i];
		}
	}
	else
	{
		for (var i=0; i<co.ds.length; i++)
		{
			if (co.ds[i].label==lbl) 
			{
				co.ds[i][this.previousSibling.name] = v;
				if (this.previousSibling.name=="rpt_r_line" && v==true) { co.ds[i].type="line"; co.ds[i].backgroundColor="#FFFFFF00";  co.ds[i].order=1; }
				if (this.previousSibling.name=="rpt_r_line" && v==false) { co.ds[i].type="bar"; co.ds[i].backgroundColor=co.ds[i].borderColor; co.ds[i].order=2; }
			}
			if (co.ds[i].rpt_r_hide==true) continue;
			i_ = ds_.length;
			ds_[i_] = co.ds[i];
		}
	}

// ds[l].type = "line"; ds[l].backgroundColor="#FFFFFF00"; 	

	// console.log ("rpt_re: ----------------------"+this.previousSibling.name+" | "+JSON.stringify (a));
	// console.log (ds_);
	//console.log (co.ds);
		
	uchart_vw (el_, lbl_, ds_, co.type, co.stacked);
}	

function urpt (el, u, a, r, m) 
{
	rpt (el);
}


