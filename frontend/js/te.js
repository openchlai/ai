var dda = [];

var aa = {};

var te = {};

var re = {};

var rk = {};

var tsu_ = 0;

var ra_ts = 0;

var elvp = null;

var elvpf = null;

var rz = {};

var FILE_UPLOAD_COUNT = 0;

var ND = ["u","uchk","uhilite","umime","uval","ufn","uaudio","ucolor","uerror","usub","uchkargs","ucal","ucalv","utime", "urpt", "pivot", "uchart", "utable", "usummary", "uv", "uredirect"];

aa["div"] = 	["className","id","innerHTML"];
aa["span"] = 	["className","id","innerHTML"];
aa["p"] = 	["className","id","innerHTML"];
aa["form"] = 	["className","id","innerHTML","method","action"];
aa["a"] = 	["className","id","innerHTML","href","target"];
aa["textarea"]= ["className","id","name","value","placeholder"];
aa["input"] = 	["className","id","name","value","type","checked","placeholder","multiple"];
aa["canvas"] = 	["className","id","width","height"];
aa["iframe"] = 	["className","id","src","width","height","frameBorder","scrolling"];
aa["img"] = 	["className","id","src","width","height"];
aa["ul"] = 	["className","id","innerHTML"];
aa["li"] = 	["className","id","innerHTML"];
aa["label"] = 	["className","id","innerHTML","for"];
aa["pre"] = 	["className","id","innerHTML"];

te["noop"] = {};



te["ur"] = { u:[null,null] };

te["s"] = { div:[null,"",null] }; 

te["l"] = { li:[null] }; 

te["sp"] = { span:[null,"",null] }; 

te["arg"] = { input:["",null,null,null,"hidden"] };

te["argc"] = { input:[null,null,null,null,"hidden"] };

te["opt"] = { div:[null], c:[ { input:[null,null,null,null,"radio",null] } ] };

te["chk"] = { div:[null], c:[ { input:[null,null,null,null,"checkbox",null] } ] }; 

te["txt"] = { div:[null], c:[ { input:[null,null,null,null,"text"] } ] }; // ["","","","","",""]

te["passwd"] = { div:[null], c:[ { input:[null,null,null,null,"password"] } ] }; 

te["ta"] = { div:[null], c:[ { textarea:[null,null,null,null] } ] };

te["txa"] = { div:[null], c:[ { input:[null,null,null,null,"text"], ev:[null,null,null] } ] }; // txt with events

te["file"] = { div:[null], c:[ { input:[null,null,null,"","file","",null] } ] }; //, ev:["","","","",null] } ] }; 

te["ac"] = { div:[null,null], ev:[null], c:[ { a:[null,"",null,"javascript:op()"] } ] };

te["aci"] = { div:[null,null], ev:[null], c:[ { a:[null,null,null,"javascript:op()"] } ] };

te["ar"] = { div:[null,null], ev:[null], c:[ { a:[null,null,"","javascript:op()"], c:[ { div:[null] } ] } ] };

te["nb"] = { s:["%0","%1"] };

te["nbe"] = { s:["x y cr","%1"] };

te["leaf"] = { div:["c r05"], s:["w01 l07 r02  y03 n gwd cb ba_","&nbsp;"] };

te["branch_footer"] = { s:["mln2 mtn13 x y15 abs gws_",""] };

te["pgto2"] = { c:
[
	{ div:["c x t03"], s:["cgr","-"] },
	{ div:["c x t03"], s:["","%3"] }
]};

te["pgto"] = { c:
[
	{ div:["c x t03"], s:["cgr","-"] },
	{ div:["c x t03"], s:["","%3"] }
]};

te["pg"] = { c: 
[
	{ div:["c"], s:["x t03","%2"] },
	{ u:[null] },
	{ div:["c"], s:["x t03","of"] },
	{ div:["c"], s:["x t03","%4"] },
	{ div:["c l"], c:[ { aci:["nav",null,"_nav",null,"prev",""], c:[ { div:[null] }, { arg:["","_a","%0"] } ] }, { s:["navl","..."] } ] },
	{ div:["c"], c:[ { ac:["nav",null,"_nav",null,""], c:[ { div:[null] }, { arg:["","_a","%0"] } ] }, { s:["navl","..."] } ] }
]};

te["pg2"] = { c: 
[
	{ div:["c t02"], c:[ { aci:["nav",null,"_nav",null,"prev",""], c:[ { div:[null] }, { arg:["","_a","%0"] } ] }, { s:["navl","..."] } ] },
	{ div:["c"], s:["x ","%2"] },
	{ u:[null] },
	{ div:["c"], s:["x ","of"] },
	{ div:["c"], s:["x ","%4"] },
	{ div:["c t02"], c:[ { ac:["nav",null,"_nav",null,""], c:[ { div:[null] }, { arg:["","_a","%0"] } ] }, { s:["navl","..."] } ] }
]};


te["arg_a"] = { arg:["","_a","%0"] };

te["arg_c"] = { arg:["","__c","1"] };

te["argf"] = { arg:["","%3","%1"] };

// ---------------------------------------------

te["kf_n"] = { p:["","o"], c: // 	
[
	{ s:["c w15 y08 cb",null] }, 
	{ li:["d"], txt:[" ba w30"," w30 x y07","",null,null] },
	{ div:["e"] }
]};

te["kf_d"] = { c:   // 		
[
	{ s:["c w15 y08 cb",null] }, 
	{ div:["d","calw"], c:
	[
		{ li:["w30 ba gw_ cb","va"], c:[ { div:[""], ev:["_dd"], c:
		[					
			{ p:["c w26 x t03","o"], c:[ { p:["","calv"], ucalv:[null,null,null] } ] }, 
			{ div:["d w02 x y content-hidden_"],  c:[ { div:["h02 w02 awb"] } ] },
			{ div:["d w02 x y content-shown_"],  c:[ { div:["h02 w02 awt"] } ] },
			{ div:["e"] }
		]} ]},
		{ div:["dd w40_ sh xx b10 ba mtn1 gw_","vdd"], ev:["_undd"], c:
		[ 
			{ div:[], c:
			[
				{ ucal:[null,null,"noop","2","Start Date", "End Date"] },
				{ div:["e"] },
				{ div:["c x"], aci:["ay","_vcal0","_cal_vw","x y tc ba_w cbl","l0","Day"] },
				{ div:["c x"], aci:["ay","_vcal1","_cal_vw","x y tc ba_w cbl","l1","Range"] },						
				{ div:["e"] }
			]}
		]}
	]},
	{ div:["e"] } 
]};

te["kf_l"] = { c:
[
	{ s:["c w15 y08 cb",null] }, 
	{ div:["d",null], c:
	[
		{ li:["w30 ba gw_ cb","va"], c:[ { div:["",null], ev:["_dd"], c: // 
		[
			{ p:["c w26 b03 r0","o"], uchk:["tag_",null,"","", null,null,null,null,null,null] }, 
			{ div:["d w02 x y content-hidden_"],  c:[ { div:["h02 w02 awb"] } ] },
			{ div:["d w02 x y content-shown_"],  c:[ { div:["h02 w02 awt"] } ] },
			{ div:["e"], c:[ { div:["g"], u:[null] } ] } // dd args
		]} ]},
		{ div:["dd mtn1 ba gw_","vdd"], ev:["_undd"], c:
		[ 
			
		]}
	]},
	{ div:["e"] }
]};

te["kf_c"] = { c: 
[
	{ s:["c w15 y08 cb",null] }, 
	{ div:["d",null], c:
	[
		{ li:["w30 ba gw_ cb","va"], c:[ { div:[""], ev:["_dd"], c:
		[
			{ p:["c w26 b03 r03","o"], uchk:["tag_",null,"","", null,null,null,null,null,null] }, 
			{ div:["d w02 x y content-hidden_"],  c:[ { div:["h02 w02 awb"] } ] },
			{ div:["d w02 x y content-shown_"],  c:[ { div:["h02 w02 awt"] } ] },
			{ div:["e"] }
		]} ]},
		{ div:["dd w30 mtn1 y ba gw_","vdd"], ev:["_undd"], c:
		[ 
			// uatgs
			{ uchk:["chk_r",null,null,"", null,null,null] }
		]}
	]},
	{ div:["e"] }
]};

te["kf_s"] = { p:["","o"], c: // 	
[
	{ s:["c w15 y08 cb",null] }, 
	{ li:["d"], txt:[" ba w30"," w30 x y07","",null,null] },
	{ div:["e"] }
]};

// ---------------------------------------------------------------------------

te["k_d"] = { div:[null,null], c:
[
	{ div:["ah","va"], ac:["","","_dd","xx y02 h03 cb",""], c:
	[					
		{ div:["c t08 b"], s:[null,null] }, 
		{ div:["d g l t03"], s:["x yy",""], c:[ { div:[null] } ] }, // da db
		{ div:["e"] }
	]},
	{ div:["dd t ba_g gw sh","vddk_d"], ev:["_undd"], c:
	[
		// { div:["l15"], c:[ { ucal:[null,null,null] }, { div:["e"] } ] },
		{ div:["x15 b10"], c: 
		[
			{ div:["c"], aci:["ay","","_cal_vw","x y tc ba_w cbl","l0","Day"] },
			{ div:["c"], aci:["ay","","_cal_vw","x y tc ba_w cbl","l1","Range"] },						
			{ div:["e"] }
		]}
	]}
]};

te["k_c"] = { div:[null,null], c:
[
	{ div:["ah","va"], ac:["","","_dd","xx y02  h03 cb",""], c:
	[
		{ div:["c t08 b"], s:[null,null] },
		{ div:["c g t03"], s:["x yy",null] }, // da db
		{ div:["e"], arg:["",null,null] }
	]},
	{ div:["dd yy sh ba_g gw cb","vddk_c"], ev:["_undd"], c:
	[ 
		// { div:[null], uchk:[null,null,null,null] }
	]}
]};
		
te["k_l"] = { div:[null,null], c: // todo: populate from list
[
	{ div:["ah","va"], ac:["","","_dd","xx y02  h03 cb",""], c:
	[
		{ div:["c t08 b"], s:[null,null] },
		{ div:["c g t03"], s:["x yy",null] }, // da db
		{ div:["e"], arg:["",null,null] }
	]},
	{ div:["dd yy sh ba_g gw cb","vddk_c"], ev:["_undd"], c:
	[ 
		{ div:[null], uchk:[null,null,null,null] }
	]}
]};

te["k_s"] = { div:[null,null], c: // 	
[
	{ div:["ah","va"], ac:["","","_dd","xx y02 h03 cb",""], c:
	[
		{ div:["c t08 b"], s:[null,null] }, 
		{ div:["c g t03"], s:["x yy",null] }, // da db
		{ div:["e"] }
	]},
	{ div:["dd","vddk_s"], ev:["_undd"], c:
	[ 
		{ div:["x y sh ba_g gw"], txt:["","","",null,null] } 
	]}
]};

te["k_a"] = { div:[null,null], c: // 	
[
	{ div:["ah","va"], ac:["","","","xx y02 h03",""], c:
	[
		{ div:["c t08 "], s:[null,null] }, 
		{ div:["c g t03"], s:["x yy",null] }, // da db
		{ div:["e"], arg:["",null,null] }
	]}
]};


te["sub"] = { u:["%0","%1"] };

te["btnwait"] = { c:[ { s:["%0","%1"] }, { arg:["tso","","12"] } ] };

te["uvpfn"] = { ufn:["uvpfn"] };

te["ufn_attach"] = { ufn:["ufn_attach"] };

// -------------------------

function op(){}

function _ID(id){ return  document.getElementById(id); }

function _element (el, tagname, cn, v)
{
	var el_ = document.createElementNS ("http://www.w3.org/1999/xhtml", tagname);
	el_.className = cn;
	el_.innerHTML = v;
	el.appendChild (el_);
}

function _rm (ev)
{
	var el = __(this); //,"va");
	var p = el.parentNode;
	p.removeChild (el);
	boo (ev)
}

function _mvup ()
{
	var p = __(this,"va");
	var p_ = p.parentNode;
	var el = p.previousSibling;
	if (el==null) return;
	console.log ("mvu "+p.id+" "+el);
	p_.removeChild (p);
	p_.insertBefore (p, el);
}

function _mvdown ()
{
	var p = __(this,"va");
	var p_ = p.parentNode;
	var el = p.nextSibling;
	if (el==null) return;
	console.log ("mvd "+p.id+" "+el);
	p_.removeChild (p);
	p_.insertBefore (p, el.nextSibling);
}

function tso ()
{
	var coll = document.getElementsByTagName ("input");
	for (var i=0; i<coll.length; i++) if (coll[i].id=="tso" && coll[i].value>-1)
	{
		var p = __(coll[i],"vs2").parentNode;
		if (p.id=="vs2") p.id="vs0";
	}
}

function tsu ()
{
	var ism = 0;
	tsu_++;
	if (tsu_==21)
	{
		tsu_=1;
		ism=1;
	}
	var coll = document.getElementsByTagName ("input"); // todo: enclose in <s> to distinguish from other inputs
	for (var i=0; i<coll.length; i++) 
	{
		if (coll[i].id=="ts" && coll[i].value>0)
		{
			coll[i].previousSibling.innerHTML = hmst (coll[i].value, ["","h","hms","0",""]);
			continue;
		}
		if (ism==1 && coll[i].id=="tm" && coll[i].value>0)
		{
			coll[i].previousSibling.innerHTML = hmsr (coll[i].value, ["","r","","1","",""," ago",""," "," ago",""]);
		}
	}
	setTimeout(tsu, 3000);
}

function _(p,id,tn,k)
{
	if (!tn) tn="p"; 
	if (!k) k="id"; 
	var coll = p.getElementsByTagName(tn);
	for (var i=0; i<coll.length; i++)
	{
		 if (coll[i][k]==id) return coll[i];
	}
	return null;
}

function __(el,id="v")
{
	var l = id.length;
	while (el.parentNode)
	{
		var id_ = el.parentNode.getAttribute ("id");
		if (id_ && id_.length>0 && id==id_.substr (0,l)) break; 
		el = el.parentNode;
	}
	return el.parentNode;
}

function grp (p,u,a,r,m)
{
	while (p.id=="vg") // ascend
	{	
		var v = null;
		var coll = p.previousSibling.getElementsByTagName ("input");
		for (var i=0; i<coll.length; i++) if (coll[i].id=="g") { v = coll[i].value; break; }
		if (v && r[u[2]]==v) { break; } // match
		p = p.parentNode.parentNode;
	}
	if (p.id!="vg") p = nd (p, te[u[0]], [], r, [0]);
	if (r[(u[4]*1)].length>0) p = nd (p, te[u[3]], [], r, [0]);
	return p;
}

function argv (p,a,k="name",skipid=null,b={})
{
	var v = "";
	var coll = p.getElementsByTagName ("input"); // console.log ("argv::: "+coll.length)
	for (var i=0; i<coll.length; i++)
	{
		var o = coll[i];
		if (o[k].length<1) continue;
		if (skipid!=null && o.id!=skipid) continue;
		v = o.value;
		if (o.type=="radio" || o.type=="checkbox")
		{
			if (!o.checked) continue; 
			// console.log (" >> "+o[k]+" | "+ b[o[k]]);
			if (a[o[k]]===undefined) { a[o[k]]=""; b[o[k]]=[]; }
			if (b[o[k]]===undefined) { b[o[k]]=[]; } // just incase
			b[o[k]][b[o[k]].length] = o; 
			if (a[o[k]].length>0) a[o[k]]+=",";
			a[o[k]]+=v;
			if (o.id=="_" && o.nextSibling.value.length>0) a[o[k]]+=":"+o.nextSibling.value 
			// console.log (" >> "+o[k]+"="+v+"   | "+o.id+" | "+a[o[k]]);
			continue;
		}
		if (o.type=="file" && a.append)
		{ 
			for (var j=0; j<o.files.length; j++) { a.append (o.name, o.files[j], o.files[j].name); }
			continue; 
		}
		if (a[o[k]]===null) { a[o[k]+"_"]=o; /*console.log (o[k]+"::");*/ }  // collect node
		if (o[k]==".id") 
		{
			// if (v.length>0)  v = "/"+v;
			a[o[k]]=v;
			continue;  
		}
		// console.log ("[argv] "+k+":"+o[k]+" | "+v+"  ("+a.args+","+a.append+")");
		if (a.args) { a.args += (o[k]+"="+encodeURIComponent(v)+"&"); continue; }
		if (a.append) { a.append (o[k], v); continue; }
		a[o[k]]=v; 
	}
	coll = p.getElementsByTagName ("textarea");
	for (var i=0; i<coll.length; i++)
	{
		var o = coll[i];
		v = o.value;
		if (a[o[k]]===null) a[o[k]]=o;  // fill gaps
		if (a.append) { a.append (o[k], v); continue; }
		a[o[k]]=v; // default: collect values 
	}

	var kb = Object.keys (b);
	for (var i=0; i<kb.length; i++) // chkbox values
	{
		var vv = b[kb[i]]; 
		v = "";
		for (var j=0; j<vv.length; j++) { if (j>0) v+=","; v+=encodeURIComponent(vv[j].value); }
		if (a.args) { a.args += kb[i]+"="+v+"&";  continue; }
		if (a.append) { a.append (kb[i], v); continue; }
	}

	// console.log ( "----> {a}" + JSON.stringify (a))

	return a;
}

function jso (p, o, k)
{
	if (k==undefined) k="name";
	var b = {};
	var coll = p.getElementsByTagName ("p");
	for (var i=0; i<coll.length; i++)
	{
		if (coll[i].id=="a" && coll[i].parentNode.id.length>0)
		{
			var t = coll[i].parentNode.id;
			var coll_ = coll[i].childNodes;
			if (o[t]==undefined) o[t]=[];
			// console.log ("--> "+t+" :"+coll_.length)
			for (var j=0; j<coll_.length; j++)
			{
				var b_ = {}
				var n = o[t].length;
				o[t][n] = {};
				argv (coll_[j], o[t][n], k, "o", b_);
				// console.log ("  jso-a ["+t+"]["+j+","+n+"] "+ JSON.stringify (o[t][n]) +" | "+ JSON.stringify (b_) )
			}
			continue;
		}
		if (coll[i].id=="o") argv (coll[i], o, k, null, b);
	}

	console.log ("[jso]  ("+p.id+"/"+p.className+") "+JSON.stringify (o)+" | "+JSON.stringify (b));
}

function rargs (r_, coll)
{
	var v = "";
	for (var i=0; i<coll.length; i++)
	{
		// console.log ("  rarg: "+coll[i].id+"="+coll[i].value);
		if (coll[i].id.length<1) continue;
		var kk = coll[i].id.split ("-");
		if (kk.length<2) continue;
		v = coll[i].value;
		r_[kk[1]] = v;
	}
	// console.log ("[rargs] "+JSON.stringify (r_));
}

function hmsr (t,a) // :r:dmyhn:17: :0:899999999:Remaining :DHm::Expred :DHm::
{
	var t_ = Math.ceil ((Date.now()/1000)); // duration in seconds
	if (ra_ts>0) t_ -= ra_ts;  	// client clock ahead
	if (ra_ts<0) t_ += (-1*ra_ts);  // client clock behind
	var d = "";
	
	var x = Math.ceil(t_-t);  // console.log (t+" "+t_+" |"+x);

	if (x>31536000) return vdt (t,["","d","dmyhnr",a[3]," "]); // >1y
		
	if (x>2419200) return vdt (t,["","d","dmhnr",a[3]," "]); // >4week

	if (x>86400) return Math.floor (x/86400)+" days ago &nbsp;&nbsp;&nbsp;" + vdt (t,["","d","hnr",a[3]," "]);

	if (x>3600) return Math.floor (x/3600)+" hours ago ";
		
	var m = Math.floor(x/60);
	return d+m+" minutes ago";
}

function hmsp (t,a)
{
	var t_ = (1*t)%86400;
	var h = Math.floor(t_/3600);
	var m = (t_%3600)/60;
	var r_ = [(""+h),(""+m),"am"];
	// console.log ("hmsp: "+t+" "+t_+" "+h+":"+m)
	if (m<10) r_[1]="0"+r_[1];
	if (h>11) 
	{ 
		r_[2]="pm";
		r_[0]=(""+(h-12));  
		if (h==12) r_[0]="12";
	}
	return r_[0]+":"+r_[1]+" "+r_[2];
}

function hmsf (t,a)
{
	var x = Math.ceil(t)
	var m = x%3600;
	var s = m%60;
	var v = "";
	if (x>=3600)
	{
		var h = Math.floor(x/3600);
		v += h+":";
	}
	m = Math.floor((m-s)/60);
	if (x>=3600 && m<10) v += a[3];
	v += m;
	if (a[2] && a[2].substr(a[2].length-1)!="s") return v;
	v += ":"
	if (s<10 && s>-1) v += "0";
	v += s; 
	return v;
}

function hmst (t,a)
{
	var ts = Math.floor(Date.now ()/1000);
	if (ra_ts>0) ts -= ra_ts;  	// client clock ahead
	if (ra_ts<0) ts += (-1*ra_ts);  // client clock behind
	return hmsf (ts-t,a);
}

function vdt (x,a)
{
	// var x = r[a[3]];
        if (x.length<1) return ""; // :d:dmyhm:1:
	var vv = x.split (";");	// console.log (a);
	var na = a[2].length; 
	var kk = {"d":0, "m":1, "y":2, "h":3, "n":4, "s":5, "r":6, "x":7};
	var c = 0;
	var s = "";
	for (var i=0; i<vv.length; i++)
	{
		if (vv[i].length<1) continue;
		if (vv[i]==0) continue;
		if (i>0) s+="&nbsp;&nbsp;to&nbsp;&nbsp;";
		var dt = new Date(1000*vv[i]);
		var v = [(""+dt.getDate()), ra["month"][(dt.getMonth()+1)][1], (""+dt.getFullYear()), (""+dt.getHours()), (""+dt.getMinutes()), (""+dt.getSeconds()), " AM", "Today "];
		if (v[3]>11) { v[6]=" PM"; }
		if (v[3]>12) { v[3]=v[3]-12; }
		//--
		for (var j=0; j<na; j++)
		{
			var k = kk[a[2].substr(j,1)];
			if (j>0 && k<4) s += a[4];
			if (k>3 && k<6) s += ":";
			if (k>3 && v[k].length==1) s += "0";
			s += v[k];
		}
		c++;
	}
	return s;
}

function vu (r,a) // ":u:f:3:4:5:6"
{
	var f = 0;
	if (a[2].length>0) f = window[a[2]] (r,a); 
	if (a[2].length<1) f = (r[a[3]]*1)>(a[4]*1) ? 1 : 0;
	//console.log ("[VU] "+r[a[3]]+"|"+f+"|"+JSON.stringify (a));
	return a[5+(f*1)];
}

function vel (r,a) // :v:table_name:col_name::enum:enum_col
{
	// console.log ("vel: "+JSON.stringify (a))

	var kk = ra[(a[2]+"_k")];
	if (kk==undefined)
	{
		if (a.length<5)  return "";
		return ra[a[4]][""][a[5]];
	}
	var k = kk[a[3]];
	if (k==undefined) return "";
	if (a[1]=="v") k = kk[a[3]][0];
	var v = r[k];
	// console.log (a[2]+":"+a[3]+" | "+JSON.stringify (r))
	if (a.length<5) return v;
	if (a[4]=="") 
	{
		if (a.length>7) v = a[7]+v; // prefix
		var o = ra[a[5]];
		if (o===undefined) return v;	
		var v_ = o[v];
		if (v_===undefined) return v;
		return v_[a[6]];
	};
	if (a[4]=="d") // date
	{
		return  vdt (v,["","d","dmy","0"," "]);
	}
	return v;
}

function ve (r,a) // ::yesno:25:2 
{
	var v = r[a[3]];
	var o = ra[a[2]];
	if (o===undefined) return "!";	
	var v_ = o[v];
	if (v_===undefined) return v;
	return v_[a[4]];
}

function valf (r,v)
{
	if (v.length<2 || !r) return v;
	if (v.substr(0,1)=="%") return r[(1*v.substr(1))]; 
	if (v.substr(0,1)!=":") return v;
	var a = v.split (":");
	
	if (a[1]=="k") // return k value
	{
		if (!ra[a[2]]) return ""
		if (!ra[a[2]][a[3]]) return ""; 
		if (a.length==4) return ra[a[2]][a[3]]; // used by applyf
		if (a.length==5 && a[4]=="p") return hmsp ([ra[a[2]][a[3]]], [,,,0,]);
		if (a.length==5 && a[4]=="h") return hmsf ([ra[a[2]][a[3]]], ["","h","hms","0",""]);
		if (a.length==5) return ra[a[2]][a[3]][a[4]]; 
		if (a.length==6) 
		{
			var v_=  ra[a[2]][a[3]][r[a[5]]]; 
			// console.log (" valf-k: "+JSON.stringify (ra[a[2]][a[3]])+" |"+r[a[5]]+" | "+v_)
			if (v_==undefined) return "";
			return v_;
		}
		return "";
	} 
	if (a[1]=="v") return vel (r,a);
	if (a[1]=="V") return vel (r,a);
	if (a[1]=="u") return vu (r,a)
	if (a.length<4) return v;
	if (r[a[3]]===undefined) return "?.";
	if (a[1]=="f") return "" + ( (r[a[3]]*1).toFixed (a[2]*1) ); 
	if (a[1]=="d") return vdt (r[a[3]],a);
	if (a[1]=="h") return hmsf (r[a[3]],a);
	if (a[1]=="t") return hmst (r[a[3]],a);
	if (a[1]=="p") return hmsp (r[a[3]],a);
	if (a[1]=="r") return hmsr (r[a[3]],a);

	return ve (r,a);
}

function val (v, a, r, m, el, k, w)
{
	var v_ = v;
	if (v===null) { v_ = a[(m[0]-1)]; m[0]--; } // pop a stack
	if (v_===null) return null;
	if (v_.length<1) return v_;
	if (v_.length>1 && r) v_ = valf (r,v_);
	if (el && k && w!=1) 
	{
		if (k=="innerHTML") 
		{
			//v_ = v_.replace (/>/gm,"&gt;"); 
			//v_ = v_.replace (/</gm,"&lt;"); 
			//v_ = v_.replace (/\n/gm,""); // line break
		}
		el[k] = v_; 
	}
	if (el && k && w==1) 
	{
		// console.log ("-ev-"+v_+ window[v_])
		el[k] = window[v_];
	}
	return v_;
}

// -------------------

function uredirect (el, u, a, r, m)
{
	console.log (u);
	window.location.href = (HOME+u[0]+u[1]);
}

function ufn (el, u, a, r, m)
{
	window[u[0]] (el, u, a, r, m); 
}

function uv (el, u, a, r, m) 
{
	var a = {args:"?", ".id":""};
	argv (el, a);
	//console.log (JSON.stringify (u)+"|"+JSON.stringify(a))
	url (el, u[0], u[1], (a[".id"]+a.args));
}

function uerror (el, u, a, r, m)
{

}

function ucolor (el, u, a, r, m)
{
	el.style.backgroundColor = u[0];
}

function uaudio (el, u, a, r, m)
{
	var s = u[0]+u[1]+u[2];
	console.log (s);
	el.innerHTML = "<audio style='width:240px;' src='"+s+"' controls preload='none'></audio>";
}

function uval_ (el, u, ja, cn)
{
	var el_ = null;
	var vv = u[1].split ("^");
	// console.log ("[uval] ("+vv.length+") "+u[1]+"|"+u[1].length)
	if (vv.length==1)
	{
		_element (el, "span", cn, u[1]);
		return
	}
	for (var j=ja; j<vv.length; j++) 
	{
		if (u[0].length==0)
		{
			if (j>ja) _element (el, "span", "micon x cd", "navigate_next"); // s += "<span class='micon x cd'>navigate_next</span>";
			_element (el, "span", (cn), vv[j]);
			continue;
		}
	
		var s = "";	
		s+="<div class='y02 cd m'><span>"+rz[u[0]][j]+"</span><span class='x micon'>navigate_next</span></div>";
		s+="<div>"+vv[j]+"</div>";
		_element (el, "div", "c r15", s);
	}
	if (u[0].length>0) _element (el, "div", "e", "");
}

function uval (el, u, a, r, m)
{
	// el.innerHTML = "";
	uval_ (el, u, 1, "");
}

function umime (el, u, a, r, m)
{
	var v = u[2];
	
	if (u[1]=="application/json")
	{
		v = atob (u[2]); 
		if (u.length>3 && u[3].length>0 && re[u[3]]) 
		{
			var ko = re[u[3]]
			var vo = null;
			try 
			{
				vo = JSON.parse (v)
			}
			catch (e)
			{
				console.error (v)
			}
			v = "Invalid Payload Received!";
			if (vo)
			{ 
				var kk = rk[u[3]]
				for (var k=0; k<kk.length; k++)
				{
					if (!vo[kk[k]]) continue;
					nd (el, te[(u[0]+"_o")], [vo[kk[k]], ko[kk[k]][1]], r, [2]); // 
//					console.log ("[umime] "+u[3]+"|"+ kk[k]+" => " + ko[kk[k]][1])
				}
				return;	
			}
		} 
	}
	
	nd (el, te[u[0]], [v], r, [1]);
}

function uhilite (el, u, a, r, m)
{
 	var txt = _(__(el,"vd").previousSibling,"txa");
 	if (!txt)
 	{
		uval (el, ["",u[0]], [], r, [0]);
 		return;
 	}
	var vv = txt.firstChild.value.split (" ");
	var cn = [];
	var w = [];
	var pk = [];
	var pos = {}
	for (var i=0; i<vv.length; i++)
	{
		if (vv[i].length<1) continue;
		var expr = new RegExp (("[ \\^]"+vv[i]+"|^"+vv[i]),'gi');
		var m = null;
		while ((m = expr.exec (u[0])) !== null)
		{
			var pi = expr.lastIndex-m[0].length;
			pos[pi] = expr.lastIndex;
			pk[pk.length] = pi;
			//console.log ("   --> ("+vv[i]+") "+expr.lastIndex+"|"+m[0]); 
		}
	}
	pk.sort ((a,b)=>{ return a-b }); // todo: check for overlap (remove overlaped pos'es)
	//console.log ("[uhilite] "+JSON.stringify (pk)+" | "+JSON.stringify (pos))
 
 	var v = u[0];
 	var v_ = "";
	var a = 0;
	var b = v.length;
	var c = 0;
	var el_ = null;
	while (a<v.length)
	{
		if (c<pk.length) b = pk[c];
		v_ = v.substring(a,b);
		uval_ (el, ["",v_], (a==0?1:0), "");
		
		if (c<pk.length)
		{
			a = b;
			b = pos[pk[c]];
			v_ = v.substring (a,b);
			uval_ (el, ["",v_], (a==0?1:0), "gws b");
		}
		a=b;
		b = v.length;
		c++;
	}
}

function uchk (el, u, a, r, m)
{	
	var a_ = [];
 	for (var i=u.length-1; i>3; i--) 
 	{
 		var v = u[i];
 		if (u[i].substr(0,1)==" ") v = u[i].substr(1);
 		a_[a_.length] = v;
 	}

	var vv = u[1].split (",");
	var vn = 0;
	if (u[1].length>0) vn=vv.length; 
	var dn = vn;
	var dk = null;
	var dv = {}; 
	if (u.length>2 && u[2].length>0 && ra[u[2]])
	{
		dv = ra[u[2]];
		dk = rk[u[2]];
		if (dk==undefined) { dk = Object.keys(dv).sort();  }
		dn = dk.length; 
		// console.log (u[2]+"  dk "+JSON.stringify (dk));
	}
	
	var fc_ = 9;
	// if (u.length>3 && u[3].length>0) fc_ = u[3]*1;
	
	var c = -1;
	for (var i=0; i<dn; i++)
	{
		var r_ = [];
		if (dk==null)
		{
			// console.log (" uchkval="+vv[i])
			var vvv = vv[i].split(":"); 
			r_ = [vvv[0],"",vv[i]];
			if (vvv.length>1) r_[1]=vvv[1];
		}
		if (dk!=null) // populated check-list
		{
			r_ = dv[dk[i]].slice (0); 		// get a copy
			r_[fc_]="";
			if (vn>0 && vv.indexOf (r_[0])>-1) r_[fc_]="1";
			// console.log ("uchk --- "+u[0]+" ["+dk[i]+"] "+vn+" "+u[1])
		}
	
		if (r_[0]=="0" && u[0]=="tag") continue; // hack: dont render tag if id==0 // tags only(sel) else show // if enum has 0 use radio
		c++;
		if (c==0 && u.length>3 && u[3].length>0 && u[3]=="^") el.innerHTML = ""; // replace txa with content
		// if (c==0 && u[0]=="tag" && u.length>2 && u[2].length<1) el.innerHTML=""; // hack: clear txa 
		
		// console.log (i+" <"+u[0]+"> "+JSON.stringify (a_)+" | "+JSON.stringify (r_));
	
		nd (el, te[u[0]], a_.slice(0), r_, [a_.length]);  
	}
}

function u (el, u_, a, r, m)
{
	var rr_ = [];
	var r_ = r;
	var n = 1;
	
	if (u_.length>1) 
	{
		n = 0;
		if (u_[1].length>0 && ra[u_[1]]) 
		{ 
			rr_ = ra[u_[1]]; 
			n = rr_.length; 
		}
		if (u_.length>2 && u_[2].length>0) // select row in object
		{
			n=0;
			if (rr_[u_[2]]) { rr_=[rr_[u_[2]]]; n=1; }
		}		
		if (n>0 && u_.length>3 && u_[3].length>0) // override 'default' content	 
		{
			if (!ra[u_[3]] || ra[u_[3]].length<1) return; 
			el.innerHTML = ""; // clear default content
		}
	}
	
	var el_ = el;
	
	if (u_.length>4 && u_[4].length>0) // order descending
	{ 
		for (var i=n-1; i>-1; i--)
		{
			if (u_.length>1) r_ = rr_[i]; 		// row i
			if (!te[u_[0]]) alert ("invalid template:"+u_[0]+"|"+JSON.stringify(a_));
			var a_ = [];
			for (j=0; j<m[0]; j++) a_[j]=a[j];
			// if (u_.length>2 && u_[2].length>0) { el_ = grp (el_, u_, a_, r_, [m[0]]);  } // grouping 
			nd (el_, te[u_[0]], a_, r_, [m[0]]); 
			continue;
		}
		return;	
	}
	
	for (var i=0; i<n; i++)
	{
		if (u_.length>1) r_ = rr_[i]; 		// row i
		if (!te[u_[0]]) alert ("invalid template:"+u_[0]+"|"+JSON.stringify(a_));
		var a_ = [];
		for (j=0; j<m[0]; j++) a_[j]=a[j];
	//	if (u_.length>2 && u_[2].length>0) { el_ = grp (el_, u_, a_, r_, [m[0]]);  } // grouping 
		nd (el_, te[u_[0]], a_, r_, [m[0]]); continue;
	}
}

function nd (p,o,a,r,m) 
{
	var el = p;
	var e = null;
	var t = null;
	var j = 0;
	var k = 0;
	var a_ = [];

	if (!o) console.log ("oi");

	for (var i in o)
	{
		if (aa[i]) e = i;
		if (te[i]) t = i;
	}
 
	if (e)
        {
                el = document.createElementNS ("http://www.w3.org/1999/xhtml", e);
                for (j=0; j<o[e].length; j++) val (o[e][j], a, r, m, el, aa[e][j]);
                p.appendChild (el);
                if (e=="input" && el.type=="text") { el.setAttribute ("autocomplete","off"); }
                if (e=="textarea")
                {
                        var st = window.getComputedStyle (el);
                        var h = st.getPropertyValue("height");
                        // console.log ("TXA: "+el.height+" | "+h+"|"+e);
                        if (h<100) el.style.height = 100; 
                }
        }
	
	if (o.ev)
	{
		//console.log ("[ev] "+JSON.stringify (o.ev)+" |"+JSON.stringify (o))
		var ev = ["onclick", "oninput", "onkeydown", "onfocus", "onblur", "onmouseover", "onmouseout"]; 
		for (j=0; j<o.ev.length; j++) val (o.ev[j], a, r, m, el, ev[j], 1); 
	}

	if (t) 
	{
		for (j=0; j<o[t].length; j++) a_[j] = val (o[t][j], a, r, m);
		if (t=="f" && a_[1].length==0) return; // skip empty filters 
		for (j=o[t].length-1; j>-1; j--) { a[m[0]]=a_[j]; m[0]++; }
		el = nd (el, te[t], a, r, m);
	}

	for (var i=0; i<ND.length; i++)
	{
		k = ND[i];
		if (!o[k]) continue;
		var u_ = [];
		for (j=0; j<o[k].length; j++) u_[j] = val (o[k][j], a, r, m);
		el = window[k] (el, u_, a, r, m, o);
	}

	var c = 0;
	if (o.c) c = o.c.length;  
	var el_ = el;
	for (var i=0; i<c; i++) 
	{
		el = nd (el_, o.c[i], a, r, m);
	}

	return el;
}

function ld (p, m, http_status) 
{
	var el = document.getElementById("lds");
	el.innerHTML="";
	for (var k in ra) 
	{
		if (k.substr (0,1)==".") rk[k.substr (1)] = ra[k];
		el.innerHTML += "<div class='y'><b>"+k+"</b>:"+JSON.stringify (ra[k])+"</div>";
	}

	for (var k in re)
	{
		if (ra[k]) re[k]=ra[k]; // update re
		if (!ra[k]) ra[k]=re[k]; // update ra		
	}

	if (!UU[m])
	{
		console.log ("Invalid target! "+m);
		return;
	}

	var uu = null;

	if (UU[m][http_status]!=undefined)  // 201,202,412,401
	{ 
		uu = UU[m][http_status];  
	}

	if (http_status==401 && UU[m][401]==undefined)
	{
		p = document.getElementById ("vv"); 
		uu = UU["login"][401];
		console.log ("!!! LOGGED OFF"); 
	}

	if (uu==undefined)
	{
		console.log ("Invalid target!!"+m+" "+http_status);
		return;
	}

	console.log (http_status+" -> "+m+":"+JSON.stringify (uu)+" @"+p.id)

	for (var i=0; i<uu.length; i++)
	{		
		var u_ = uu[i];
		var p_ = p;
		// if (!ra[u_[1]]) continue;
		if (u_.length>2 && u_[2].length>0 && p_.id.substr (0,u_[2].length)!=u_[2])
		{
			// console.log ("ascend "+p_.id+"("+p_.className+") -> "+u_[2]);
			p_ = __(p_, u_[2]);  // ascend 
			// console.log ("ascend: "+p_.id+" -> "+u_[2]);
		}
		if (u_.length>3 && u_[3].length>0) 
		{
			// console.log ("descend "+p_.id+"("+p_.className+") -> "+u_[3]);
			p_ = _(p_, u_[3]); // descend
			if (u_[3]=="vp" && u_[0]!="noop") vp (p_);
			if (u_[3]=="vp" && u_[0]=="noop") document.getElementById ("vp").style.display = "none";
		}
		if (p.id=="vs0")
		{
			var cn  = "vs2";
			if (ra.errors) cn = "vs3";
			p.parentNode.id = cn;
			p_ = p.parentNode.firstChild;
			setTimeout (tso, 10000); // wait ten seconds for ami update, else show button for user to try 
		}
		 // console.log ("ld::nd: "+p_.id+" |"+JSON.stringify (u_));
		p_.innerHTML = ""; // clear 
		var a_ = [];
		var m_ = [0];
		// for (var j=ra.a[i].length-1; j>-1; j--) { a_[m_[0]]=ra.a[i][j]; m_[0]++; }
		// console.log (p_.id+" | "+u_[0]+" "+u_[1]);
		nd (p_, {u:[u_[0],u_[1]]}, a_, [], m_);
	}

	ra["auth_nb"] = [];

	if (tsu_==0) 	{ tsu (); tsu_=1; }
}

function ld_audio (p, u, x)
{
	console.log ("[ld audio] "+p.id+" "+u+" "+x.status) 
	const audioURL = URL.createObjectURL (x.response);
	p.innerHTML = "<audio controls></audio>";
	p.firstChild.src = audioURL;
	p.firstChild.play ()
}

function url_progress (ev)
{
//    console.log (ev.type+": "+ev.loaded+" bytes transferred");
}

function url (p, u, m, a="", data=null, l=0, o=null, meth="GET")
{
        if (l==0)
        {
                var le = document.createElementNS ("http://www.w3.org/1999/xhtml", "div");
                le.className = "xx t02 s go sh'";
                le.id = "loadn";
                le.innerHTML = "";
                p.insertBefore (le, p.firstChild); // todo: ajax loader on p or el?
        }
        if (l==2 || l==3)
        {
                p.className="savn";
                var nb = _(p,"nb");
                if (nb) nb.innerHTML = "";
        }
        var x = new XMLHttpRequest ();
        if (l==4)
        {
                p.className="savn";
                x.addEventListener('loadstart', url_progress);
                x.addEventListener('load', url_progress);
                x.addEventListener('loadend', url_progress);
                x.addEventListener('progress', url_progress);
                x.addEventListener('error', url_progress);
                x.addEventListener('abort', url_progress);
        }
        if (m.length>0) m+="/";
        x.open (meth, (APIPATH+m+a), true);
        x.responseType = 'blob';
        if (o && u=="login")
        {
                var s = btoa (o.user+":"+o.pass);
                x.setRequestHeader('Authorization','Basic ' + s);
                o = null;
        }
	 if (o)
        {
                // console.log ("-------JJ");
                x.setRequestHeader('Content-Type','application/json');
                data = JSON.stringify (o);
        }
        x.onload = function (ev)
        {
                // console.log ("XHR content-type: "+x.getResponseHeader("Content-Type"))

                if (x.getResponseHeader("Content-Type").substr (0,6)=="audio/")
                {
//                      console.log ("XHR content-type: "+x.getResponseHeader("Content-Type"))
                        //console.log (ev.target)
                        ld_audio (p,u,x);
                        return;
                }
                x.response.text().then (text =>
                {
                        ra = JSON.parse (text);
                        if (l==2 || l==4) p.className="";
                        // if (l==4) ; // set timeout 
                        ld (p,u,x.status);

			// todo: if l==1 and loadn.count>1 then append n-1 loaders for pending queries
                });
        };
        x.onerror = function (error)
        {
                console.error (error)
        //      // window.alert ("Error: " + ev.target.status);
        };
        // todo: progress bar (useful for file upload)
        x.send (data);
}

function postj (el,k,mode=2) 
{
        var id = "v"
        var u = el.id.split ("-");
        if (u.length>2) id=u[2] 
        var p = __(el,id);
        var o = {}; 
        jso (p,o,k);
        url (p, u[0], u[1], o[".id"], null, mode, o, "POST");
}

function urargs (el, p)
{
	//console.log ("urargs("+el.id+")----------------------------")
	var u = el.id.split("-");

	if (re[u[1]]!=undefined)
	{
		ra = [];
		for (var k in re) ra[k]=re[k]; // reset ra
		var r_ = ra[u[1]][0].slice (0)
		var coll_ = el.firstChild.lastChild.getElementsByTagName ("input");
		rargs (r_, coll_);
		p.innerHTML = "";
		nd (p, te[u[0]], [], r_, [0]); 
		return;
	}

	var a = {args:"?", ".id":""};	
	argv (el.lastChild,a);
	url (p, u[0], u[1], (a[".id"]+a.args));
}

function uvpfl (p, m=1)
{
	var a = {args:"?", ".id":""};
	var coll = p.firstChild.lastChild.childNodes;
	var u = coll[0].value.split ("-");
	var v = coll[1].value.split (",");
	argv (p.childNodes[1], a);	// filter args 
	for (var i=0; i<v.length; i++) 	// todo: check if checked ; else find checked
	{
		p = p.lastChild.childNodes[v[i]].childNodes[1];
	}

	if (m==1) coll[2].value =  Math.floor(Date.now ()/1000); // update filter_ts
	//console.log ("uvpfl("+coll[0].value+")----------------------------"+p.previousSibling.value+","+coll[2].value)
	if (p.previousSibling.value>=coll[2].value) return;	// skip if no change in  filter_ts
	p.previousSibling.value = coll[2].value;

	if (coll[0].value.length<1) return;

	if (u.length==1)
	{
		p.innerHTML = "";
		nd (p, te[u[0]], [], [], [0]); 
		return;
	}

	if (p.childNodes.length>0)
	{
		argv (p.firstChild, a);
		if (p.firstChild.id=="vrpt") p = p.childNodes[1];
	}
	url (p, u[0], u[1], (a[".id"]+a.args));
}

function uvpf (el)
{
	var u = el.id.split ("-");
	var o = {}; 	
	var p = __(el);
	var pvf = elvpf;
	elvpf = null;
	jso (p, o);
	ra[u[1]] = o;
	p = document.getElementById ("vp");
	p.style.display = "none";
	p.innerHTML = "";
	pvf.firstChild.innerHTML = "";
console.log (el.id);
	nd (pvf.firstChild, te[u[0]], [], [], [0]);
	uvpfl (pvf.parentNode)
}

function uvpfn (el, u, a, r, m)
{
	el.style.display = "none"; // hide vp
	el.innerHTML = "";
	if (!elvp.firstChild) { elvp=null; return; }
	var u_ = elvp.firstChild.value.split ("-");
	el = elvp;
	elvp = null;
	//console.log ("uvpfn: "+u_)
	if (u_.length>2 && u_[2].length>0) el = __(el, u_[2]); 	// ascend
	if (u_.length>3 && u_[3].length>0) el = _(el, u_[3]); 	// descend
	if (u_.length>4 && u_[4]!="!") el.innerHTML = "";
        if (u_.length>4 && u_[4]=="!" && el.childNodes.length>0)
        {
                var el_ = document.createElementNS ("http://www.w3.org/1999/xhtml", "div");
                el.insertBefore (el_, el.firstChild);
                el = el_;
        }
	nd (el, te[u_[0]], [], r, [0]);
}

function uvp ()
{
	if (elvp.id.length<1) { elvp=null; return; }
	var u = elvp.id.split ("-");
	var p = elvp;
	if (u.length>2 && u[2].length>0) p = __(p, u[2]); // ascend
	if (u.length>3 && u[3].length>0) p = _(p, u[3]);  // descend
	if (u.length>4 && u[4].length>0) p.innerHTML = "";

	//console.log ("uvp ("+elvp.id+") " + p )
	
        if (re[u[1]]!=undefined)
	{
		nd (p, te[u[0]], [], [], [0]);
		return;
	}

	var a = {args:"?", ".id":""};
	argv (elvp, a);
	//console.log (" >> uvp "+elvp.id+" | "+ JSON.stringify (a))
	url (p, u[0], u[1], (a[".id"]+a.args));
}

function vp (p)
{
	var h = window.innerHeight;
	var w = window.innerWidth;
	var h_ = document.body.scrollHeight;
	var w_ = document.body.scrollWidth;
	// console.log (h+" "+h_)
	if (h_>h) h=h_;
	if (w_>w) w=w_;
	p.style.height = h
	p.style.width = w
	p.style.display = "block";
	p.innerHTML = ""; // todo: doc-fragment	
 	window.scrollTo(0, 0); 
	// console.log (p.className)
} 

// ---

function _nd (ev)
{
	ra = [];
	for (var k in re) ra[k]=re[k]; // reset ra

	var u = this.id.split("-");
	var p = this;
	if (u.length>2 && u[2].length>0) p = __(p,u[2]);
	if (u.length>3 && u[3].length>0) p = _(p,u[3]);
	if (u.length>4 && u[4].length>0) p.innerHTML = ""; // todo: doc-fragment
	
	var r_ = ra[u[1]][0].slice(0); // get a copy
	rargs (r_, this.firstChild.lastChild.childNodes, r_);
	
	//console.log ("[nd] "+u[0]+" "+u[1]+" | "+JSON.stringify (r_));
	nd (p, te[u[0]], [], r_, [0]);
	boo(ev);
}

function _u (ev) 
{
	var u = this.id.split ("-");
	var v = "v";
	if (u.length>2 && u[2].length>0) v = u[2];
	var p = __(this,v); // ascend
	if (u.length>3 && u[3].length>0) p = _(p, u[3]); // descend
	var a = {args:"?", ".id":""};
	argv (__(this),a);
	url (p, u[0], u[1], (a[".id"]+a.args));
	boo(ev);
} 

function _nav (ev) 
{
	var u = this.id.split ("-");
	var p = __(this);
	var a = {args:"?", _c:null, __c:null};
	argv (this,a);
	console.log ("[nav] "+p.id)
	//var coll = p.firstChild.getElementsByTagName ("p");
	//for (var i=0; i<coll.length; i++) if (coll[i].id=="vc") { argv (coll[i],a);  }
	argv (p.childNodes[2].firstChild, a)
	//console.log (a);
	if (a.__c_) a._c_=a.__c_; 
	var r = a._c_.value;
	if (this.firstChild.id=="prev") r = a._c_.value*-1;
	a.args += "_o="+r; // aka
	// console.log (JSON.stringify (a));
	this.parentNode.id="ld";
	url (p, u[0], u[1], a.args);
	boo(ev)
}

function _del (ev) // delete record
{
	// todo: js confirm
	var u = this.id.split ("-");
	var el = __(this,"va");
	var p = el.parentNode;
	var o = {};
	argv (this, o);
	if (this.id.length<1) 
	{
		p.removeChild (el);
		return;
	}
	url (el, u[0], u[1], o[".id"], null, 2, o, "POST");
	boo(ev);
}

function _postj (ev)
{
	postj (this,"name");
	// boo(ev);
}

function _postji (ev) 
{
	postj (this,"id");
	boo(ev);
}

function _postjb (ev) 
{       
        postj (this,"name",3);
        boo(ev);
}

function _uvpf () { uvpf (this); }

function _uvpd (ev)
{	
	if (!this.firstChild) return;
	if (this.firstChild.id!="vddvw" && this.firstChild.id!="vddvf") return; // block non-vddvw from closing
	this.style.display = "none";
	if (this.firstChild.id=="vddvf") uvpf (this.firstChild.lastChild.firstChild.firstChild);
	if (elvp) uvp ();
}

function _uvp (ev)
{
	var p = document.getElementById ("vp");
	p.style.display = "none";
	p.innerHTML = "";
	if (elvp) uvp ();
	boo(ev);	
}

function _uvw ()
{
	var p = __(this,"vfvw");
	p.parentNode.previousSibling.firstChild.checked = true;
}

function _vpf ()
{
	var p = document.getElementById ("vp");
	var u = this.id.split ("-"); 
	var o = {}; 
	elvpf = __(this,"vb").nextSibling;
	jso (elvpf, o);
	ra[u[1]] = o;
	vp (p);
	nd (p, te[u[0]], [], [], [0]);
}

function _vp (ev)
{
	var p = document.getElementById ("vp");
	var u = this.id.split ("-");
	elvp = null;
	if (u.length>2) elvp = this.nextSibling;
	vp (p);
	urargs (this, p);
	boo(ev);
}

function _vw (ev)
{
	var u = this.id.split ("-");
	var p = __(this,"vftab").parentNode.nextSibling;
	this.previousSibling.checked=true;
	p.firstChild.checked = true;
	// if (u.length<3 && p.childNodes[1].childNodes.length>0) return; // dont repopulate
	p.childNodes[1].innerHTML = ""
	urargs (this, p.childNodes[1]);
	boo (ev)
}

function _tab (ev) 
{
	var u = this.id.split ("-");		
	var coll = __(this,"vb").parentNode.lastChild.childNodes;
	var p = coll[this.previousSibling.value];		
	this.previousSibling.checked = true;
	p.firstChild.checked = true;
	
	if (this.previousSibling.previousSibling) // set uvpf params
	{	
		var p_ = __(this,"vftab");
		var coll_ = p_.firstChild.lastChild.childNodes; // uvpf params
		coll_[0].value = this.previousSibling.previousSibling.id
		coll_[1].value = this.previousSibling.previousSibling.value;
		// todo: align rpt_menu top-rigt of vb
		if (p.childNodes[1].childNodes.length>0)
		{
			uvpfl (p_, 0);
			return;
		}
		// else load normarly
	}
	
	if (u.length<2) return; // skip non-res
	if (u.length<3 && p.childNodes[1].childNodes.length>0) return; // dont repopulate
	urargs (this, p.childNodes[1]);
}

// --------------------

function _print ()
{
	window.print ();
}

function _xlsx ()
{
	var p = __(this,"vb").nextSibling;
	var a = {args:"?", ".id":""};
	argv (this, a);
	argv (p, a);
	var s = APIPATH+this.id+a.args+"xlsx=1";
	console.log (s);
	window.location.href = s;
	//url (p.childNodes[1], u[0], u[1], (""+a.args));
}

function _csv ()
{
	var p = __(this,"vb").nextSibling;
	var a = {args:"?", ".id":""};
	argv (p, a);
	var s = APIPATH+this.id+a.args+"csv=1";
	console.log (s);
	window.location.href = s;
	//url (p.childNodes[1], u[0], u[1], (""+a.args));
}

function _download ()
{
	var p_ = __(this,"vftab");
	var coll_ = p_.firstChild.lastChild.childNodes; // get active-tab args
	var z = coll_[1].value.split (",");
		
	console.log ("[data download] "+coll_[1].value)
	
	if (z[0]=="0")
	{
		var p = __(this,"vb").nextSibling;
		var a = {args:"?", ".id":""};
		argv (this, a);
		argv (p, a);
		var s = APIPATH+this.id+a.args+"xlsx=1";
		console.log ("[data download]"+s);
		window.open (s, "report");
		// window.location.href = s;
		return;
	}
	
	var p = p_;
	for (var i=0; i<z.length; i++) // descend sub-trees
	{
		if (!p.lastChild) break;
		p = p.lastChild.childNodes[z[i]].childNodes[1];
	}
	
	rpt_download (p.childNodes[1]);
}

function _file_download ()
{
	var a = {args:"?", ".id":""};
	argv (this, a);
	var s = APIPATH+this.id+"/"+a[".id"]+a.args;
	console.log ("file_download: "+s);
	window.location.href = s;
}

function ufn_attach (el, u, a, r, m)
{
	var u = el.parentNode.nextSibling.id.split ("-");
	var p = __(el)
	var o = {};
	o["file_id"] = r[0];
	jso (el.parentNode.nextSibling, o);
	// console.log (JSON.stringify (o));
	url (p, u[0], u[1], "", null, 2, o, "POST");
}

function ufile (el,f)
{
	console.log("Name: " +f.name+" Type: " + f.type +"Size: " + f.size);
	el.nextSibling.innerHTML = f.name; // todo: mutliple files
	var u = el.id.split ("-");
	var data = new FormData ();
	argv (el.parentNode, data);
	url (__(el), u[0], u[1], "", data, 3, null, "POST");

	/*
	var reader = new FileReader();
	reader.onload = function (ev) 
	{
		var contents = ev.target.result;
		console.log("File contents: ||" + contents);
	};
	reader.onerror = function(ev) 
	{
	    console.error("File could not be read! Code " + ev.target.error.code);
	};
	reader.readAsDataURL (f); */
}

function _file_upload (ev)
{
	__(this,"va").className = ""; // unhide
	var ff = this.files;
	for (var i=0; i<ff.length; i++)
	{
		ufile (this, ff[i]);
	}
}

function _file_dialog (ev)
{
	var u_ = this.id.split ("-");
	var p = _(__(this,u_[2]),u_[3]);
	var r_ = re["r_"][0].slice (0);
	var coll_ = this.firstChild.lastChild.childNodes;
	rargs (r_, coll_)
	var el = nd (p, te[u_[0]], [], r_, [0]);
	el = __(el,"va");
	el.firstChild.firstChild.click ();
	boo (ev)
}

