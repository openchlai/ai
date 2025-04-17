argv

url

_post() { args ( js) }

_vpf

_vp

_vw
	
_tab

_nav 

_u

------------------

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

function _postj (ev)
{
	var p = __(this,id);
        var o = {}; 
        var u = this.id.split ("-");
        var id = "v"
	if (u.length>2) id=u[2] 
        jso (p,o); 
        url (p, u[0], u[1], o[".id"], null, 2, o, "POST");
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
	var p = __(this,"vf").parentNode.nextSibling;
	this.previousSibling.checked=true;
	p.firstChild.checked = true;
	if (u.length>1)
	{
		p.childNodes[1].innerHTML = ""
		urargs (this, p.childNodes[1]);
	}
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



