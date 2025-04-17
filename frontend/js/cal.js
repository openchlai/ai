
/*
te["5minute_r"] = { div:["c w03","min"], ac:["aa bb_bl_d w07 ","","_cal_sel","xx y cb","%1"], c:[ { div:["","vsel"], c:[ { arg:["cal_5minute","","%0"] }, { arg:["cal_5minute_txt","","%1"] } ] } ] };

te["minute_r"] = { div:["c w05"], ac:["ay","","_sel","xx tt b05 cb",""], c:
[
	{ s:["c","%2"] },
	{ div:["e"], c:[ { arg:["minute","","%0"] }, { arg:["minute_txt","","%2"] } ] }
]};

te["hhmm"] = { div:["n","vh"], c:
[
	{ div:["c w05 l"], s:["","&#160;"] }, // ac:["","time_pre","_cal","v b tc",";"] },
	{ div:["c w03_"], c:
	[
		{ div:["","va"], c:[ { txa:["","w03 y03 gwg cb tc","cal_hour_txt","","::hour:3:2","_dd","_ro",""] }, { arg:["cal_hour","","%3"] } ] },
		{ div:["dd b20","vdd"], ev:["_undd"], c:[ { div:["ba_ba ga w18"], c:[ { uchk:["hour_r","","hour"] }, { div:["e"] } ] } ] } 
	]},
	{ s:["c x01 y cb b",":"] },
	{ div:["c w03_"], c:
	[
		{ div:["","va"], txa:["","w03 y03 gwg cb tc","cal_5minute","","%4","_dd","_ro",""] }, 
		{ div:["dd b20","vdd"], ev:["_undd"], c:[ { div:["ba_ba ga cb w12"], c:[ { uchk:["5minute_r","","5minute"] }, { div:["e"] } ] } ] } 
	]},
	{ p:["c w03 l03 y04 cb tc","mer","::hour:3:4"] },
	{ div:["e"] }
]};*/


// ----------------------------

te["tag_time"] = { li:["bd cb",""], c:
[
	{ s:["c x y",null] },
	// { ac:["c ao ll","","_uchkf","x y cb","&Cross;"] },
	{ arg:["o",null,null] },
	{ div:["e"] } 
]};

te["merides_r"] = { div:["d r10"], c:
[
	{ input:["g","","_mer","%0","radio","%9"] }, 
	{ ac:["opty","","_meridies","x08 y04 bd6 gws cb","%0"] }
]};

te["hour_r"] = { div:["c w03 t r05"], c:
[ 
	{ input:["g","","_hour","%1","radio","%9"] }, 
	{ ac:["opty","","_hour","xx y04 cb bd8","%1"] } 
]};

te["day_of_week_r"] = { div:[], ac:["ay","","_sel","xx y cb",""], c:
[
	{ s:["c","%2"] },
	{ div:["e"], c:[ { arg:["dayofweek","","%0"] }, { arg:["dayofweek_txt","","%2"] } ] }
]};

te["hhmmaa"] = { form:[], c:
[
	{ div:["w21 x y"], uchk:["hour_r","%0","hour_am"] },
	{ div:["xx t15 b05"], c:
	[
		{ s:["c x y cd","Minutes:"] },
		{ div:["c w02"], ac:["ay","pre","_mm","x y",""], c:[ { div:["w02 h01_ awl"] } ] },
		{ div:["c w04"], txa:["ba","w04 y04 tc cb m","","_minutes","%1","","_mm",""] },
		{ div:["c w02"], ac:["ay","nx","_mm","x y",""], c:[ { div:["w02 h01_ awr"] } ] },
		{ uchk:["merides_r","%2","meridiesr"] },
		{ div:["e"] }
	]},
	{ arg:["%3","",""] }
]};

function time_val (el)
{
	var p = __(el); 
	var a = { "_minutes":null };
	var b = {};
	argv (p,a,"name",null,b);

	var minu = 1*a["_minutes_"].value;
	var s = "";
	if (el.id=="pre") minu = (1*a["_minutes_"].value)-1;
	if (el.id=="nx") minu = (1*a["_minutes_"].value)+1;
	if (minu<10) s="0";
	if (minu<0) minu = 0;
	if (minu>59) minu = 59;
	a["_minutes_"].value = minu;
	
	// console.log ("   [timeval] "+JSON.stringify (b));

	var h_ = b["_hour"][0].value*1; // Object.keys (a["_hour"])[0] *1; // a["_hour"]*1;
	var mer_ = b["_mer"][0].value; // Object.keys (a["_mer"])[0]; // a["_hour"]*1;

	var s_ = h_+":"+s+a["_minutes_"].value+" "+mer_;

	if (h_==12 && mer_=="am") h_=0;
	var v_ = (h_*3600)+(minu*60);
	if (h_!=12 && mer_=="pm") { v_ = (v_*1)+43200; } // TODO: round of 11:59:xx to 11:59 during dialplan qh query

	console.log (" time_val: "+p.id+" | "+s_+" | "+v_ +"  "+a["_mer"]+"  // "+JSON.stringify (a))

//	console.log ("  >> "+v_+" |"+h_+"| "+minu);
	var p_ = _(p.previousSibling,"timev");
	p_.innerHTML = "";
	nd (p_, te["tag_time"], [v_, p.firstChild.childNodes[2].id, s_], [], [3]);
}

function _meridies (ev)
{
	this.previousSibling.checked = true;
	time_val (this);
}

function _mm (ev)
{
	time_val (this);
}

function _hour (ev)
{
	this.previousSibling.checked = true;
	time_val (this);
}

function utime (el, u_, a, r, m)
{
	var ts = (1*u_[1])%86400;
	var h = Math.floor(ts/3600);
	var m = ts%3600;
	var r_ = [(""+h), (""+m), "am", u_[0]];
	if (m<10) r_[1]="0"+r_[1];
	if (h>11) { r_[0]=(""+(h-12)); r_[2]="pm"; }
	// console.log (r_)
	var el_ = nd (el, te["hhmmaa"], [], r_, [0]);
//	el_.parentNode.className = "_"+r_[2];
//	console.log (el_.parentNode.tagName)
}

// ------------------------------------

te["tag_calv"] = { div:["c b05 r05","va"], c:[ { div:["gb bd cw",""], c:
[
	{ s:["c x07 y",null] },
	{ ac:["c aa","","_rm","x y bdr cws","&Cross;"] }, // delete tag
	{ arg:["o",null,null] },
	{ div:["e"] } 
]} ]};

te["month_r"] = { div:["c w05","month"], ac:["aa bb_bl_d w15 ","","_cal_sel","xx y cb","%1"], c:[ { div:["","vsel"], c:[ { arg:["cal_month","","%0"] }, { arg:["cal_month_txt","","%1"] } ] } ] };

te["day_blank"] = { div:["c w02_ tc"], s:["y04","&#160;"] };

te["day"] = { div:["c w02_ ay"], ac:["%1","day_a","_day","x04 y04 tc cb","%0"] };

te["cal"] = { div:["c","%7"], c: 
[
	{ arg:["%5","","%6"] },

	{ div:["lbl"], s:["xx b10 b tc","%8"] },

	{ div:["w19 t02","va"], c:
	[
		{ div:["c w02"], ac:["ay","yr_pre","_cal","x y",""], c:[ { div:["w02 h01_ awl"] } ] },
		{ div:["c w04"], txa:["","w04 y tc cb m","cal_yr","","%0","","",""] },
		{ div:["c w02"], ac:["ay","yr_nx","_cal","x y",""], c:[ { div:["w02 h01_ awr"] } ] },
	
		{ div:["c w02"], ac:["ay","month_pre","_cal","x y",""], c:[ { div:["w02 h01_ awl"] } ] },
		{ div:["c w06"], c:
		[
			{ div:["","va"], c:[ { txa:["","w06 y cb tc m","cal_month_txt","","::month:1:2","_dd","_ro",""] }, { arg:["cal_month","","%1"] } ] },
			{ div:["dd b20","vdd"], ev:["_undd"], s:["ba_ba_ ga sh_ w15",""], uchk:["month_r","","month"] } 
		]},
		{ div:["c w02"], ac:["ay","month_nx","_cal","x y",""], c:[ { div:["w02 h01_ awr"] } ] },
		{ div:["e"] }
	]},

	{ div:["w17_ cb  y08"], c:
	[ 
		{ s:["c w02_ y04 tc gws cr","S"] }, { s:["c w02_ y04 gws tc","M"] }, { s:["c w02_ y04 gws tc","T"] }, { s:["c w02_ y04 gws tc","W"] }, { s:["c w02_ y04 gws tc","T"] }, { s:["c w02_ y04 gws  tc","F"] }, { s:["c w02_ y04 tc gws cr","S"] }, { div:["e"] } 
	]},

	{ div:["w17_ b10"], c:
	[ 
		{ p:["w17_","days"] },  // days
		{ div:["e"], arg:["cal_day","","%2"] } 
	]},

	{ div:["x"] } // time select
]};

function cal_val (p)
{
	var fmt = ":d:dmy:0: :0";
	if (p.firstChild.lastChild.childNodes.length>0) fmt = ":d:dmyhn:0: :0";
	var coll_ = p.childNodes;
	var v_ = coll_[0].firstChild.value;
	if (p.className=="_vcal1" && coll_[1].firstChild.value.length>0) v_+=";"+coll_[1].firstChild.value;
	var p_ = _(p.parentNode.previousSibling, "calv");
	p_.innerHTML = ""
	nd (p_, te["tag_calv"], ["%0", coll_[0].firstChild.id, fmt], [v_], [3]);
	
	if (p.parentNode.nextSibling && p.parentNode.nextSibling.id && p.parentNode.nextSibling.id=="fn")
	{
		window[p.parentNode.nextSibling.firstChild.id] (p.parentNode.nextSibling.firstChild, [v_]);
	}
}

function days (p,r,f,n) // load days
{
	p.innerHTML = "";
	var dt = new Date (r[0],(r[1]-1),1);
	var cn = dt.getDay ();
	for (var i=0; i<cn; i++)
	{
		nd (p,te["day_blank"],[],[],[0]);
	}

	var today = new Date ();
	var dy = -1;
	if (dt.getFullYear()==today.getFullYear() && dt.getMonth()==today.getMonth()) dy=(today.getDate()-1);
	for (var i=0; i<n; i++) 
	{
		var s = ("d"+cn);
		if (f==1 && i==(r[2]-1)) s += " d7"; 
		if (i==dy) s += " d8"; 
		nd (p,te["day"],[],[((parseInt(i)+1)+""), s],[0]); 
		cn++;
		if (cn>6) cn=0;
	}
}

function cal (el,id)
{
	var dm = [0,31,28,31,30,31,30,31,31,30,31,30,31];
	var o = {};
	var p = __(el,"vcal");
	var coll = p.getElementsByTagName ("input"); //_a (p,o,"id"); // collect all variables but skip dd _cal_sel args
	for (var i=0; i<coll.length; i++) if (coll[i].id.length>0 && coll[i].parentNode.id!="vsel") o[coll[i].id] = coll[i];
	var v = id.split("_");
	if (v[1]=="pre") o[("cal_"+v[0])].value -= 1; 
	if (v[1]=="nx") o[("cal_"+v[0])].value = parseInt (o[("cal_"+v[0])].value)+1;
	if (v[1]=="a") o[("cal_"+v[0])].value = el.firstChild.innerHTML;
	if (v[0]=="yr" || v[0]=="month") // recalc yr,month
	{
		var yr = o["cal_yr"];
		var m = o["cal_month"];
		if (m.value<1) { m.value=12; yr.value-=1; }
		if (m.value>12) { m.value=1; yr.value=parseInt(yr.value)+1; }
		o["cal_month_txt"].value = re["month"][m.value][2]; 	
	}
	var r = [o["cal_yr"].value, o["cal_month"].value, o["cal_day"].value]
	if (r[1]==2 && (((r[0] % 4 == 0) && (r[0] % 100 != 0)) || (r[0] % 400 == 0))) dm[2]=29;
	if (dm[r[1]]<r[2]) 
	{
		o["cal_day"].value = dm[r[1]];
		r[2] = o["cal_day"].value;
	}

	var ts = new Date (o["cal_yr"].value, (o["cal_month"].value-1), o["cal_day"].value); 
	if (o["cal_hour"]!=undefined) 
	{
		ts = new Date (o["cal_yr"].value, o["cal_month"].value, o["cal_day"].value, o["cal_hour"].value, o["cal_5minute"].value); 
	}

	days (_(p,"days"), r, 1, dm[r[1]]);

	p.firstChild.value = (""+(Math.floor(ts.getTime() / 1000)));

	cal_val (p.parentNode);
}

function _day (ev) 
{	
	var _p = __(__(this,"vdd"),"vdd")
	cal (this, this.id);
	boo(ev);
}

function _cal (ev) 
{ 
	cal (this, this.id); 
	boo(ev); 
}

function _cal_sel (ev)
{ 
	var o = {}; 
	sel (this,"id",o);
	if (this.parentNode.id=="hr") _(__(this,"vh"),"mer").innerHTML=re["hour"][o.cal_hour.value][4];
	cal (__(this,"vdd"), this.parentNode.id); 
	boo(ev);
}

function _cal_vw ()
{
	this.parentNode.parentNode.className = this.id;
	cal_val (this.parentNode.parentNode);
}

function cali (el, k, v, tmf, i, lbl) 
{
	if (v==undefined || v==null || v==0) v="";
	var dm = [0,31,28,31,30,31,30,31,31,30,31,30,31];
	var f = 0;
	var dt = new Date();
	if (v.length>0 && v>0) { dt = new Date ((1*(v+"000"))); f=1; }
	var r = [(""+dt.getFullYear()), (""+(dt.getMonth()+1)), (""+dt.getDate()), (""+dt.getHours()), (""+dt.getMinutes()), k, v, ("vcal"+i), lbl];
	// if ((r[3]*1)<10) r[3] = "0"+r[3];
	if ((r[4]*1)<10) r[4] = "0"+r[4];
	var el_ = nd (el, te["cal"], [], r, [0]);
	if (r[1]==2 && (((r[0] % 4 == 0) && (r[0] % 100 != 0)) || (r[0] % 400 == 0))) dm[2]=29;
	days (el_.previousSibling.firstChild, r, f, dm[r[1]]);
	nd (el_, te[tmf], [], r, [0]);
}

function ucalv (el, u_, a, r, m)
{
// console.log ("UCALV  "+ JSON.stringify (u_))
	if (u_[2].length<1 || u_[2]<1) return;
	var v = valf ([u_[2]], u_[0].substr(1));   // console.log (" ucal: "+v+" | "+u_[2]+","+u_[0])
	u_[0] = v;
	nd (el, te["tag_calv"], [u_[2], u_[1], u_[0]], [], [3]);
}

function ucal (el, u_, a, r, m) // ucal:["expiry","","noop","1"]
{
	var vv = u_[1].split (";");	
	var cn = "_vcal0"
	if (vv.length>1 && (u_[3]*1)>1)  cn = "_vcal1";
	el.className = cn;
	cali (el, u_[0], vv[0], u_[2], 0, u_[4]); 
	if ((u_[3]*1)>1) cali (el, u_[0], vv[1], u_[2], 1, u_[5]); 

}

