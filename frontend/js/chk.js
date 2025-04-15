
te["tagv"] = { div:["c mtag"], s:[null,""], uval:["",null] };

te["taga"] = { div:["c","va"], s:["mtag gb cw",""], c: // .f.f.f
[
	{ div:["d w02_"], ac:["abs w02_ ao",null,"_uchk","x y04 cs n tc","&Cross;"] },
	{ div:["x y04 mr3"], uval:["",null] },
	{ div:["e"], c:[ { input:["g","o",null,null,"checkbox","1"] }, { arg:["fullname_id-2","",null] } ] }
]}; 

te["tag"] = { div:["c","va"], s:["mtag gb cw",""], c: 
[
	{ div:["d w02_"], ac:["abs w02_ ao",null,"_usel","x y04 cs n tc","&Cross;"] },
	{ div:["x y04 mr3"], uval:["",null] },
	{ div:["e"], c:[ { input:["g","",null,null,"checkbox","1"] }, { arg:["fullname_id-2","",null] } ] }
]};

te["tag_"] = { div:["c","va"], s:["mtag gb cw",""], c:
[
	{ div:["d w02_"], ac:["abs w02_ ao",null,"_uchk","x y04 cs tc","&Cross;"] },
	{ div:["x y04 mr3"], uval:["",null] },
	{ div:["e",null], c:[ { input:["g","_",null,null,"checkbox","1"] }, { arg:["","",null] } ] }
]}; 

te["tagf"] = { div:["c ml mt mb ba_b cb","va"], c: 
[
	{ div:["c x07 y"], uval:["",null] },
	{ ac:["c l ab","","_uchkf","x y n cd","&Cross;"] },
	{ input:["g","_",null,"%0","checkbox","1"] },
	{ arg:["","",null] },
	{ div:["e"] } 
]};

te["f"] = { div:["c"], c: // 
[
	{ div:["c t"], s:["x y cd",null] }, 
	{ ac:["c l t","","_uchkp","x y n cg","&Cross;"] },
	{ p:["c l02 r10 ","o"], uchk:["tagf",null,"","",null,null,null] },
]};

te["chk_r"] = { div:[], c: 
[
	{ input:["g",null,"","%0","checkbox","%9"] },
	{ ac:["r ay","","_chk","xx cb",""], c:
	[ 
		{ div:["c w01_ t"], s:["chk",""] },
		{ s:["c x y ",null] },
		{ s:["d x y ",null] },
		{ div:["e"], c:[ { arg:["id-0","","%0"] } ] }
	]}
]};

// ------------------------------

function chk_del (el, k, v)
{
	var u_ = el.id.split ("-");
	var o = {"is_linked":"0"};
	var o_ = {}
	jso (__(el,"ve"), o_);
	o[u_[2]] = o_[".id"];
	o[k] = v;
	console.log ("[chk del] "+u_[0]+","+u_[1]+" "+JSON.stringify (o))
	url (__(el,"va"), u_[0], u_[1], "", null, 0, o, "POST");
}

function uchkargs (el, u_, a_, r_, m_)
{
	var a = { }
	var coll = el.parentNode.previousSibling.getElementsByTagName ("input");
	for (var i=0; i<coll.length; i++)
	{
		var o = coll[i];
		if (o.name.length<1) continue;
		var k = o.name;
		if (o.parentNode.id.length>0) k = o.parentNode.id;
		if (a[k]===undefined) a[k]={};
		a[k][o.value] = "1";
	}
	console.log ("[uchkargs] "+u_[0]+" | "+JSON.stringify (a))
	ra[u_[0]] = a;
}

function chk (el)
{
	var v = true
	if (el.checked) v = false;
	el.checked = v;
	return v;
}

function _uchkp (ev)
{
	var el = this.parentNode;
	var p = el.parentNode;
	var pv = __(this,"vf");
	p.removeChild (el);
	uvpfl (pv.parentNode);
	boo(ev)
}

function _uchkf (ev)
{
	var el = this.parentNode;
	var p = el.parentNode;
	var pv = __(this,"vf");
	p.removeChild (el);
	if (p.childNodes.length==0) pv.firstChild.removeChild (p.parentNode);
	uvpfl (pv.parentNode);
	boo(ev)
}

function _uchk (ev)
{
	var el = __(this);
	var p = el.parentNode;
	var b = __(p,"va").nextSibling; // eval selu fn 
	var k = el.firstChild.lastChild.firstChild.name;
	var k_ = el.firstChild.lastChild.id;
	var v = el.firstChild.lastChild.firstChild.value;
	var r_ = ra["r_"][0].slice(0);
	var coll_ = el.firstChild.lastChild.childNodes;
	r_[0] = v;
	rargs (r_, coll_);
	var coll = b.getElementsByTagName ("input");
	if (k_=="") k_=k;
	for (var i=0; i<coll.length; i++) // uncheck chk_r
	{
		if (coll[i].id==k_ && coll[i].value==v) 
		{ 
			coll[i].checked = false; 
			break; 
		}
	}

	// console.log (" -> "+JSON.stringify (r_))

	if (b.nextSibling && b.nextSibling.id=="sub") sel_sub (b.nextSibling.childNodes, r_[2], false);

	boo (ev);

	if (this.id.length>0)
	{
		chk_del (this, k, v);
		return;
	}

	p.removeChild (el);
}

function _chk_all (ev)
{
	var el = this.firstChild.firstChild;
	var p = __(this);
	var coll = p.getElementsByTagName("input");
	for (var i=0; i<coll.length; i++)
	{
		// chk (coll[]);
	}
	boo (ev);
}

function _chkg ()
{
	var f = chk (this.previousSibling);
	var s = "none";
	if (f==true) s="block";
	this.parentNode.nextSibling.style.display = s;
}

function _chk ()
{
	var b = __(this,"vdd");
	var p = b.previousSibling;
	var u_ = p.parentNode.id.split ("-"); 
	var p_ = _(p, u_[3]);
	var k = this.previousSibling.id;
	var v = this.previousSibling.value;
	var f = chk (this.previousSibling);
	var a_ = [];
	var r_ = re[u_[1]][0].slice (0);
	var el = null;
	var coll = p_.getElementsByTagName ("input");

 	for (var i=u_.length-1; i>3; i--) a_[a_.length]=u_[i];
	r_[0] = v;
	rargs (r_, this.firstChild.lastChild.childNodes);

	for (var i=0; i<coll.length; i++) // find tag
	{
		if (coll[i].name==k && coll[i].value==v) { el=coll[i]; break; }
		if (coll[i].parentNode.id==k && coll[i].value==v) { el=coll[i]; break; }
		// console.log ("  --> "+coll[i].name+":"+coll[i].value+" | "+el)
	}

	console.log ("[chk] "+ JSON.stringify (u_)+" "+el);	

	if (b.nextSibling && b.nextSibling.id=="sub") sel_sub (b.nextSibling.childNodes, r_[2], f);
	
	if (f==false) // remove tag
	{
		if (el==null) return;
		el = __(el);		
		if (el.firstChild.firstChild.firstChild.id.length>0)
		{
			chk_del (el.firstChild.firstChild.firstChild, k, v);
			return;
		}
		p_.removeChild (el);
		return;
	}
	
	if (el!=null) return;
	
	nd (p_, te[u_[0]], a_, r_, [a_.length]);	
}

