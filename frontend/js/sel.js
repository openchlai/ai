
te["sel_r"] =  { ac:["aa","","_sel","x20 y cb","%1"], c:[ { arg:[null,"","%0"] }, { arg:[null,"","%1"] } ] };

function boo (ev) { ev.stopPropagation (); }

function _ro () { return false; }

function sub (el, u, r, v, v_, f)
{
	console.log ("    [sub-check] ("+u[0]+") " + v +"==" + v_); 
	var vv = v.split (",");
	var vv_ = v_.split (",");
	for (var j=0; j<vv.length; j++)
	{
		var vvv = vv[j].split ("^");
		for (var k=0; k<vvv.length; k++)
		{
			var id = vvv[k].split(":")[0];
			for (var j_=0; j_<vv_.length; j_++)
			{	
				if (id==vv_[j_] || (vv_[j_]=="*" && id.length>0))
				{
					console.log ("    [sub] ("+u[0]+") "+vvv[k]+"=="+vv_[j_]+"  | "+j+","+j_);
					if (f==true && el.firstChild && el.firstChild.id==u[0]) continue; // skip if already set
					el.innerHTML = "";
					if (f==false) continue;
					nd (el, te[u[0].split(",")[j_]], [], r, [0]);
					return;
				}
			}
		}
	}	
}

function usub (el, u, a, r, m)
{
	sub (el, u, r, u[2], u[3], true);
}

function sel_sub (coll, v, f, m=0)
{
	for (var i=0; i<coll.length; i++)
	{
		var u_ = coll[i].id.split ("-");
		var p_ = _( __(coll[i],u_[2]), u_[3]);
		var r_ = re[u_[1]][0].slice (0); 
		if (p_.nextSibling && p_.nextSibling.id=="rargs")
		{
			var k = p_.nextSibling.value.split ("-");
			var kk = re[(k[0]+"_k")]
                	r_[kk[k[1]][0]] = v.split(":")[0];
		}
		if (m==1) p_.innerHTML="";
		sub (p_, u_, r_, v, coll[i].value, f);
	}
}

function usel (el_) // load txa
{
	var u = el_.id.split ("-");
	var el = __(el_);
	var p = el.parentNode;
	var b = __(p,"va").nextSibling; 
	var r_ = ra["r_"][0].slice(0); // get a copy
	var coll = el.firstChild.lastChild.childNodes;
	rargs (r_, coll);
	p.removeChild (el);

	if (u[0].length>0) // /*p.childNodes.length==0 &&*/) // load txa
	{
		// console.log ( "USEL: "+u[0]+" #"+el.id+" cn:"+el.className+" n:"+coll.length+"|"+JSON.stringify (r_))
		p.innerHTML = "";
		nd (p, te[u[0]], [], [], [0]);
		p.firstChild.firstChild.focus ();
	}
	
	if (b.nextSibling && b.nextSibling.id=="sub") sel_sub (b.nextSibling.childNodes, r_[2], false, 1);
}

function sel (el, r_) 
{
	var b = __(el,"vdd");
	var p_ = b.parentNode;
	var u_ = p_.id.split ("-");
	if (u_.length>2 && u_[2].length>0) p_ = __(p_, u_[2]);
	if (u_.length>3 && u_[3].length>0) p_ = _(p_, u_[3]);

	if (!r_) r_ = ra[u_[1]][0].slice(0); // get a copy
	var coll = el.firstChild.lastChild.childNodes;
	rargs (r_, coll);
 
 	var a_ = [];
 	for (var i=u_.length-1; i>3; i--) a_[a_.length]=u_[i]; 	
	p_.innerHTML = "";
	nd (p_, te[u_[0]], a_, r_, [a_.length]);
	
	if (b.nextSibling && b.nextSibling.id=="sub") sel_sub (b.nextSibling.childNodes, r_[2], true, 1);
	
	if (b.nextSibling && b.nextSibling.nextSibling && b.nextSibling.nextSibling.id=="fn")
	{
		window[b.nextSibling.nextSibling.firstChild.id] (b.nextSibling.nextSibling.firstChild, r_);
	}
}

function undd (p_)
{
	var b = null;
	for (var i=0; i<dda.length; i++) 
	{
		// todo: remove zombie
		if (dda[i][0]==p_)
		{
			var b = dda[i][1];
			var o = {};
			b.style.display = "none";
			if (b.previousSibling && b.previousSibling.firstChild) b.previousSibling.firstChild.className = ""
			dda.splice (i,1);
			
			if (b.id=="vdd_rpt")
			{
				// console.log ("vdd_rpt");
				rpt (__(b,"vrpt").nextSibling);
			}
			break; 
		}
	}
	return b;
}

function dd (b,f) 
{ 
	var p_ = __(b,"vdd");
	if (f==1)
	{
		var b_ = undd (p_);
		if (b_==b && f==1) { console.log ("undd self"); return; } // self
	}
	// console.log ("dd ++")
	b.style.display = "block";
	if (b.previousSibling && b.previousSibling.firstChild) b.previousSibling.firstChild.className = "content-shown"
	var coll = b.previousSibling.getElementsByTagName ("p");
	var i=0;
	for (i=0; i<coll.length; i++) if (coll[i].id=="txa") { coll[i].firstChild.focus(); break; }
	var i=0;
	for (i=0; i<dda.length; i++) if (dda[i][0]==p_) break;
	dda[i] = [p_,b];
	// document.body.style.height = document.body.scrollHeight; // maintain height to reduce flicker
}

function _usel (ev) 
{
	usel (this);
	boo (ev); 
}

function _sel (ev) 
{ 
	sel (this); 
	undd (__(__(this,"vdd"),"vdd")); 
}

function _undd (ev) {  undd (this); boo (ev); } 

function _dd (ev) 
{ 
	var p = __(this,"va");
	var b = p.nextSibling;
	dd (b,1); 
	if (this.id && this.id.length>0 && b.childNodes.length<1)
	{
		var u = this.id.split ("-");
		var a = {args:"?", ".id":""}; 
		if (u.length>2) 
		{
			p = p.lastChild; // select different parameters if lsh
			u = p.id.split ("-");
		}
		argv (p,a,"id");
		url (b, u[0], u[1], (a[".id"]+a.args+"&_c=10"));
	}
	boo (ev); 
}

function _g (ev)
{
	var p = __(this,"vg");
	var b = p.nextSibling;
	console.log ("_g: "+p.firstChild.className)
	if (p.firstChild.className=="content-shown") 
	{
		p.firstChild.className = "content-hidden";                
		b.style.display = "none"; //pa.className = "g";
		return;
	}
	p.firstChild.className = "content-shown";
	b.style.display = "block"; // pa.className = "";
	if (this.id && this.id.length>0 && b.childNodes.length<1)
	{
		var u = this.id.split ("-");
		var a = {args:"?", ".id":""};
		argv (this,a,"id");
		url (b, u[0], u[1], (a[".id"]+a.args));
	}
	boo (ev); 
}

function _uky (ev)
{
	// this.value = "";
}

function _ky (ev) // autocomplete query -- todo: handle arrow-keys
{
	var p = __(this,"va");
	var b = p.nextSibling
	var u = p.firstChild.id.split ("-");
	var a = {args:"?_c=10&", ".id":""};
	argv (p.firstChild,a,"id"); // argv (__(this,"txa"),a,"id");
	// console.log (" ky: "+u[0]+"-"+u[1]+"|"+JSON.stringify (a))
	if (b.id.substr (0,3)=="vdd") dd (b);
	
	if (u.length>2) // set active tab for lsh
	{
		console.log ("lsh: "+b.childNodes.length)
		b.childNodes[0].childNodes[1].firstChild.checked=true;
		b.childNodes[1].childNodes[1].firstChild.checked=true;
		b = b.childNodes[1].childNodes[1].childNodes[1];
	}
	
	url (b, u[0], u[1], (a[".id"]+a.args));
}

function _optky (ev)
{
	var p = __(this,"va");
	var u = p.firstChild.id.split ("-");
	var a = {args:"?_c=10&", ".id":""};
	this.previousSibling.checked = true;
	argv (p,a,"id");
	console.log (" optky: "+JSON.stringify (a))
	url (p.nextSibling, u[0], u[1], (a[".id"]+a.args));
}

function _opt ()
{
	this.previousSibling.checked = true;
	if (this.parentNode.lastChild.id=="sub") 
	{
		var el = this.parentNode.lastChild.firstChild;
		var u_ = el.id.split ("-");
		var p = _( __(el,u_[2]), u_[3]);
		var r_ = re[u_[1]][0].slice (0); 
		p.innerHTML = "";
		sub (p, u_, r_, this.previousSibling.value, el.value, true);
	}
}


