var chan_t = {};

var ATI_COUNT = 0;

var ATI = 
{
	"CHAN_TS":1,
	"CHAN_UNIQUEID":2,
	"CHAN_CHAN":3,
	"CHAN_CALLERID_NUM":4,
	"CHAN_CALLERID_NAME":5,
	"CHAN_CONTEXT":6,	
	"CHAN_EXTEN":7,
	"CHAN_ACTION_ID":8,

	"CHAN_STATE_ORIG":9,	
	"CHAN_STATE_DOWN":10, 
	"CHAN_STATE_DIAL":11, 	
	"CHAN_STATE_RING":12,	
	"CHAN_STATE_UP":13,
	"CHAN_STATE_QUEUE":14, 	
	"CHAN_STATE_CONNECT":15, 	
	"CHAN_STATE_HANGUP":16,
	"CHAN_STATE_MUTE":17,
	"CHAN_STATE_HOLD":18,
	"CHAN_HOLD_TIME":19,
		 	
	"CHAN_BRIDGE_ID":20,
	"CHAN_BRIDGE_COUNT":21,
	"CHAN_UNREAD":22,
	"CHAN_HANGUP":23,

	"CHAN_UID_2":24,
	"CHAN_CID_2":25,

	"CHAN_SRC":26,
	"CHAN_MSG":27,
	"CHAN_BREAK_REASON":28,
	"CHAN_VECTOR":29,

	"CHAN_STATUS_":31,
	"CHAN_STATUS_TXT_":32,
	"CHAN_STATUS_TS_":33,
	"CHAN_STATUS_TS_TXT_":34
};

te["ati_session"] = { p:["","%2"], s:["",""], c: 
[ 
	{ input:["g","","sbl","%2","radio"] },
	{ li:["sbr xx y mt1","va"], ev:["_ati_popup"], c: 
	[ 
		{ div:[], c: 
		[
			{ s:["c x y n micon","chat"] },
			{ s:["c x y g","%26"] },  // src
			{ s:["c x y","%25"] }, 	  // src_address
			{ s:["d x y s",""] },	  // status-ts-txt
			{ arg:["ts","",""] }, 	  // status-ts
			{ div:["e"] }
		]},			
		{ div:[], c:
		[
			{ s:["c x y w21 h01_ s",""] },			// last msg
			{ div:["d t02"], s:["x07 y02 bd16 gr cw s","0"] },	// unread count
			{ div:["e"], c:[ { arg:["","src","%26"] }, { arg:["","src_uid","%2"] }, { arg:["","src_usr","%4"] }, { arg:["","src_uid2","%24"] },{ arg:["","src_address","%25"] }, { arg:["","src_vector","%29"] }, { arg:["","src_callid","%20"] }, { arg:["","src_ts","%1"] }, ] } 
			
		]},
	]},
	{ p:["g"], uaudio:["/helpline/images/new_msg.ogg","",""] },
	{ div:[] }
]};

te["nti_ended"] = { s:["t cd tc","Notification Closed"] };

te["nti_btns"] = { c:
[
	{ div:["d x"], c:
	[
		{ input:["g","","sbr","1","radio"] },
		{ ac:["x","","_activity_close","x cb",""], c:
		[
			{ s:["d x t02 h","&Cross;"] },
			{ s:["d x y","Close"] },
			{ div:["e"] }
		]},
	]},
	{ div:["d"], s:["",""], c:
	[
		{ ac:["btn","nti_end","_ati_end","x cb",""], c:
		[
			{ s:["c x t tc","Close Notification"] },
			{ s:["c x y03 w02 h02 h2 ma bd16 cb tc abtn micon","last_page"] },

			{ div:["e"] }
		]},
		{ s:["x y go cw savl","..."] }
	]}, 
	// { s:["d b x20 yy","0:00"] },
	{ div:["e"] }
]};

te["ati_ended"] = { s:["t cd tc","Chat Closed"] };

te["ati_btns"] = { c:
[
	{ div:["d x"], c:
	[
		{ input:["g","","sbr","1","radio"] },
		{ ac:["x","","_activity_close","x cb",""], c:
		[
			{ s:["d x t02 h","&Cross;"] },
			{ s:["d x y","Close"] },
			{ div:["e"] }
		]},
	]},
	{ div:["d w11"], s:["",""], c:
	[
		{ ac:["btn","ati_end","_ati_end","x cb",""], c:
		[
			{ s:["c x t tc","End Chat"] },
			{ s:["c x y03 w02 h02 h2 ma bd16 cb tc abtn micon","last_page"] },
			{ div:["e"] }
		]},
		{ s:["x y go cw savl","..."] }
	]}, 
	// { s:["d b x20 yy","0:00"] },
	{ div:["e"] }
]};

te["ati_toolbar"] = { div:["ma w20",":v:activities:src_callid"], c: //  
[
	{ input:["g","ati_toolbar","barr","1","radio","1"] },
	{ li:["abs mtn37 ao w20 bd"], ev:["_activity_show"], s:["gr bd cw",""], c:
	[

		//{ div:["c yy bd gr cw"], c:
		//[
			{ s:["c w05 x y",":v:activities:src::case_src:1"] },
			{ s:["c w08 y tc b",":v:activities:src_address"] },		
			{ s:["d w05 x y tr",""] },
			{ arg:["ts","",":v:activities:src_ts"] }, 
			{ div:["e"] }
		//]},
		//{ div:["e"] }
	]}
]};


te["ati_available"] = { div:[], s:["xx y cd","Text Queues On"] };

// ---------------------------------------------------------------------

function _ati_end ()
{
	var p = __(this,"vb").lastChild;
	var o = {"close":"close", "src_msg":"*closed*"};
	argv (p, o);
	// bconsole.log (o)
	// url (this.parentNode, this.id, "msg_end", "", null, 2, o, "POST");
	url (this.parentNode, this.id, "messages", "", null, 2, o, "POST");
}

function ati_ld_unread (ch)
{
	var coll = document.getElementById ("vv").childNodes;
	if (!coll[1].firstChild) return;
	console.log ("ati_ld_unread |"+ch[20]+"|"+coll[1].firstChild.id+"|")
	if (coll[1].firstChild.id!=ch[20]) return;
	var p = _(coll[6].childNodes[1].childNodes[1].lastChild, "msgs")
	url (p.previousSibling, "activity_messages", "messages", ("?src="+ch[7]+"&src_callid="+ch[20]+"&_c=30"));
}

function ati_popup (el, f=0)
{
	var coll = document.getElementById ("vv").childNodes;
	var r_ = re["r_"][0].slice(0);
	var a = {};
	var k = re["activities_k"];
	
	argv (el, a);
	r_[k["src"][0]] = a.src;
	r_[k["src_uid"][0]] = a.src_uid;
	r_[k["src_address"][0]] = a.src_address;
	r_[k["src_uid2"][0]] = a.src_uid2;
	r_[k["src_usr"][0]] = a.src_usr;
	r_[k["src_vector"][0]] = a.src_vector;
	r_[k["src_callid"][0]] = a.src_callid;
	r_[k["src_ts"][0]] = a.src_ts;
	
	if (re["case_src"][a.src][11]=="reporter_phone") r_[k["src_address"][0]] = _phone_fmt (a.src_address);
	
	if (f==0 && coll[1].childNodes.length>0 && coll[1].firstChild.id.length>0) // vw is occupied
	{
		var a_ = {};
		argv (coll[6].childNodes[1].childNodes[1].firstChild.lastChild, a_)
		//console.log (a)
		//console.log (a_)
		if (a.src_callid==a_.src_callid) // is same session -- update src args only and select new ati_session
		{
			var p_ = coll[6].childNodes[1].childNodes[1].firstChild.lastChild;
			p_.firstChild.innerHTML = "";
			nd (p_.firstChild, te["activity_vw_id_args"], [], r_, [0]);
			el.firstChild.firstChild.checked = true; 		// hilite call-notif			
		}
		// notify (el); // create transient notification 
		return
	}
	
	ra = {};
	for (var k_ in re) ra[k_]=re[k_];
		
	if (f==0 && a.src=="escalation") return; // dont popupb coz notif will clear on activity fetch

	// todo: get current checkted tab in coll[6]

	el.firstChild.firstChild.checked = true; 		// hilite call-notif			

	coll[1].innerHTML = ""; 			
	coll[6].childNodes[1].childNodes[1].innerHTML = "";
	coll[6].childNodes[1].firstChild.checked = true; 	// show tab
	
	var s = "-1?src=" + a.src + "&src_uid=" + a.src_uid + "&src_vector="+a.src_vector+"&src_callid="+a.src_callid;
	if (r_[k["src_address"][0]].length>0)  
	{
		s += "&src_address="+r_[k["src_address"][0]];
	}

	var u_ = re["case_src"][a.src];
	nd (coll[1], te["ati_toolbar"], [], r_, [0]); // show toolbar	
	nd (coll[6].childNodes[1].childNodes[1], te["activity_vw_id"], [u_[8],"1",""], r_, [3]);
	url (coll[6].childNodes[1].childNodes[1].lastChild, u_[9], "activities", s);	
}

function _ati_popup ()
{
	ati_popup (this.parentNode.parentNode, 1)
}

function ati_status (ch)  // down, dial(earliest unread ts), ring(latest unread ts), up(last assigned), que (latest assigned), connect
{
	var st = 10;
	for (var i=10; i<19; i++) 
	{
		if (ch[i].length<1) continue; 
		st = i;
		if (i==ATI.CHAN_STATE_HANGUP) break; // chan hangup
	}
	return st;
}

function atis_pop (ts)
{
	var k = Object.keys (chan_t);
	for (var i=0; i<k.length; i++)  // remove closed, hangup channels
	{
		var id = k[i];
		if (chan_t[id].ts==ts) continue;
		console.log  ("[ati] pop "+id+" "+chan_t[id].ts+","+ts+" | "+chan_t[id].el)
		if (chan_t[id].el && chan_t[id].el.parentNode) 
		{
			var pe = chan_t[id].el.parentNode;
			var el = chan_t[id].el;
			pe.removeChild (chan_t[id].el); 
		}
		delete chan_t[id];
	}
}

function atis (o,k,ts)
{
	var pu = document.getElementById ("call_sessions");
	var user_cid = document.getElementById ("user_cid").value;
	var c = [0,0,0,0,0,0,0];
	var unread_tot = 0;
	var ch_agent = null;
	
	for (var i=k.length-1; i>-1; i--)
	{
		var ch = o[k[i]];
		
		if (ch[ATI.CHAN_STATE_HANGUP].length>0) continue; // skip hangup'ed channels
		
		if (ch[0].length>0) 		 // agent session chan
		{
			c[0]++; 
			if (user_cid.length>0 && user_cid==ch[0]) ch_agent = ch;
			//chani ("chan_agent", pa, ch, ts); 
			continue;
		}
		//console.log ("[atis] "+user_cid+"|"+ch[ATI.CHAN_CALLERID_NUM]+","+ch[ATI.CHAN_CONTEXT] +i+"of"+ k.length)
		if (ch[ATI.CHAN_CONTEXT]=="agtk" && ch[ATI.CHAN_CALLERID_NUM]==user_cid)
		{
			// console.log ("[ati] "+ch[3])
			var el = _(pu, ch[2]); // find matching activity
			var el_ = el;	
			if (el==null)
			{
				el = nd (pu, te["ati_session"], [], ch, [0]);
				el = el.parentNode.parentNode;
				chan_t[ch[2]] = { "el":el, "ts":ts };
				// console.log ("[ati] new: "+ch[2]+" "+ch[4]+","+ch[6]+" |"+el) 
				ati_popup (el);
			}
			chan_t[ch[2]].ts=ts;
			var st = ati_status (ch);
			var coll = el.firstChild.childNodes[1].childNodes;
			var unnotified = (ch[22]*1) - (coll[1].childNodes[1].firstChild.innerHTML*1) //
			unread_tot += (ch[22]*1)
			console.log ("[ati] status="+st+" unread="+ch[22] +" unnotified="+unnotified)
			coll[0].childNodes[3].innerHTML = hmst (ch[st], ["","","hms","","","",""]);;
			coll[0].childNodes[4].value = ch[st];
			coll[1].childNodes[0].innerHTML = ch[27];
			coll[1].childNodes[1].firstChild.innerHTML = ch[22];
			coll[1].childNodes[1].style.display = (ch[22]*1)>0?"block":"none";
			if (unnotified!=0) 
			{
				el.firstChild.childNodes[2].firstChild.play ();
				if (el_ !=null) ati_ld_unread (ch);	
			}
		}	
	}

	var p_ = document.getElementById ("ati_status");
	var id_ = "noop";
	var r_ = [];
	if (ch_agent!=null) { id_ = "ati_available"; r_=ch_agent; }
	p_.innerHTML = "";
	nd (p_, te[id_], [], r_, [0]);
	ATI_COUNT = unread_tot;
	notifs ();
}

function ldati (o)
{
        var ts = (Date.now ()/1000);
        var k = Object.keys (o);
        re["channels"] = o;
        atis (o, k, ts);        
        atis_pop (ts);
}

