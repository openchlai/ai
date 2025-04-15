
var chan_a = {};

var AMI = 
{
	"CHAN_TS":1,
	"CHAN_UNIQUEID":2,
	"CHAN_CHAN":3,
	"CHAN_CALLERID_NUM":4,
	"CHAN_CALLERID_NAME":5,
	"CHAN_CONTEXT":6,
	"CHAN_EXTEN":7,
	"CHAN_ACTION_ID":8, 
	"CHAN_STATE_UP":13,
	"CHAN_STATE_QUEUE":14,	
	"CHAN_STATE_CONNECT":15,
	"CHAN_STATE_HANGUP":16,
	"CHAN_STATE_HOLD":18,

	"CHAN_CBO_TS":20,
	"CHAN_CBO":21,
	"CHAN_CBO_UNIQUEID":22,
	"CHAN_CBO_CID":23,

	"CHAN_XFER_TS":24,
	"CHAN_XFER":25,	
	"CHAN_XFER_UNIQUEID":26,
	"CHAN_XFER_CID":27,

	"CHAN_ORIG":36,
	
	"CHAN_CONTEXT_MASQ":43,
	"CHAN_EXTEN_MASQ":44,
	
	"CHAN_UNIQUEID_2":45,
	"CHAN_CHAN_2":46,
	"CHAN_CID_NUM_2":47,
	
	"CHAN_SIPCALLID":50,
	"CHAN_BRIDGE_ID":51,
	
	"CHAN_CAMPAIGN_ID":53,  
	"CHAN_CAMPAIGN_WRAPUP":54,
	
	"CHAN_PROMPT_TS0":67,
	
	"CHAN_VECTOR":74,
	"CHAN_EVENT":76,
	"CHAN_EVENT_N":77,

	"CHAN_SIPID_JS_":80,
	"CHAN_STATUS_":81,
	"CHAN_STATUS_TXT_":82,
	"CHAN_STATUS_TS_":83,
	"CHAN_STATUS_TS_TXT_":84
	
	
};

re["ami_k"] = AMI;

re["chan_action"] = 
{
"2":["2","Dialing.","cd","ts"], // cb_dial
"3":["3","Resume..","cd","ts"], // cb_action
"4":["4","Transfer.","cd","ts"], // cb_action
"5":["5","Conference.","cd","ts"], // cb_action
"init":["init","Dialing.","cd","ts"], // wait for actual status
"dialing":["dialing","Dialing...","cd","ts"], // wait for actual status
"offline":["offline","Extension is Offline","cr",""],
"busy":["busy","Busy","cr",""],
"noanswer":["noanswer","No Answer","cr",""],
"consult":["consult","Consult Ended","cg",""],
"add":["add","Added To Call","xx y03 bd gg cw",""],
"axfer":["axfer","Transfer Successful","xx y03 bd gg cw",""],
"bxfer":["bxfer","Blind Transfer...","xx y03 bd go cw",""],
};

te["chan_add_done"] = { div:[], c:
[
	{ div:["c x y"], s:["::chan_action:1:2","::chan_action:1:1"] },
	{ div:["e"] }
]};

te["chan_add_ld"] = { div:["gw","action"], c:
[
	{ div:["c xx y07"], s:["::chan_action:1:2","::chan_action:1:1"] },
	{ s:["d xx y07",":t:ms:0: "] }, // ts-txt // :h:ms:5
	{ arg:["::chan_action:1:3","","%0"] }, // ts
	{ div:["e"] }
]};

te["chan_add_btns"] = { c:
[
	{ div:["c x y"], c:[ { ac:["ao btn","chan_add_ld-chan-4","_add_action","x y w08 gws cb s tc","Transfer"] }, { s:["y bd b savl","..."] } ] },
	{ div:["c x y"], c:[ { ac:["ao btn","chan_add_ld-chan-5","_add_action","x y w08 gws cb s tc","Conference"] }, { s:["y bd b savl","..."] } ] },
	{ div:["c l y"], c:[ { ac:["ao btn","chan_add_ld-chan-3","_add_action","x y04 w08 ba cb s tc","Resume"] }, { s:["y bd b savl","..."] } ] },
	{ p:["e","o"], c:[ { arg:["","chan3",":V:ami:CHAN_CHAN"] }, { arg:["","exten",":V:ami:CHAN_EXTEN_MASQ"] }, { arg:["","chan_ts",":V:ami:CHAN_TS"] } ] },
	{ p:["x","nb"] }
]};

// ---

te["call_add_msg"] = { s:["::chan_action:0:2","::chan_action:0:1"] };
					
te["call_add_ld"] = { div:["","add_ld"], c: 
[ 
	{ div:[], c:
	[
		{ s:["c x07 y b","%2"] }, // xten
		{ div:["e"] }
	]},
	{ div:[""], c:
	[
		{ div:["c x07 y07"], s:["::chan_action:1:2","::chan_action:1:1"] },
		{ s:["d xx y07",":t:ms:0:"] }, // ts-txt
		{ arg:["::chan_action:1:3","","%0"] }, // ts
		{ div:["e"] }
	]}
]};

te["call_add_user"] = { div:["","user_ls-users"], c:[ { p:["","txa"], c:
[ 
	{ div:[], c:[ { input:["w37 xx tt b05","usn__","usn__","","text",""], ev:["","_ky","","_uky"] } ] }, 
]} ]};

te["call_add_form"] = { div:["","ve"], c: 
[
	{ s:["x y","Select User"] },
	{ div:["t"], c:[ { p:["c x","nb"] }, { div:["e"] } ] },
	{ div:["y"], c:
	[
		// { div:["c x"], c:[ { div:["ba_b w15"], c:[ { input:["w15 x y","","add",""] } ] } ] },

		{ div:["c w23","tag-r_--o-call_add_user-%1-user_id-%0-"], c:
		[
			{ li:["gws_ b02","va"], c:[ { div:["","user_ls-users"], ev:["_dd"], c: // ls
                	[
                        	{ p:["c w20","o"], c:
                        	[ 
                        		{ u:["call_add_user","r_"] }, 
                        		// { uchk:["tag",null,"","^", null,null,null,null,null] } // set if there is a default user
                        	]},
                        	{ div:["d w02 x t"],  c:[ { div:["h02 w02 awb"] } ] },
                        	{ div:["e"], c:[ { arg:["_c","","10"] }, { arg:["exten","",""] }, { ufn:["users_online_ufn"] } ] } // limit to users who are online
                	]} ]},
                	{ div:["dd w30 gw ba_b","vdd"], ev:["_undd"] },
		]},
		
		// { div:["d x"], c:[ { ac:["ag btn","call_add_ld-chan","_add_dial","x15 y gws cb tc","Invite"] }, { s:["y b savl","..."] } ] },
		{ div:["d x"], c:[ { ac:["ay btn","call_add_ld-chan","_add_dial","x15 y ba cb tc","Dial"] }, { s:["y b savl","..."] } ] },
		{ div:["e"] }
	]},
]};
	
te["call_add_form_main"] = { div:["w30 ma bd sh__ gw xx yy","vddvw"], ev:["_undd"], c:
[
	{ div:["","vp_add"], c:
	[
		{ s:["c x yy h3","Add To Call"] },
		{ div:["d x"], ac:["","","_uvp","x y h cb","&Cross;"] },
		{ div:["e"] }
	]},
	{ div:["",":V:ami:CHAN_UNIQUEID"], c:[ { div:["","init"], s:["x y g","..."] } ] },
	{ div:["","cba"] } // show add-chan status 
]};

te["call_btns"] = { c: 
[	
	{ arg:["","",":v:activities:src_callid"] }, // sipid needed to invoke call actions
	{ div:["","va"],  c:
	[	
		{ div:["d w09 gnws x call_ended_"], c:
		[
			{ input:["g","","sbr","1","radio"] },
			{ ac:["d x t","","_activity_close","x y03 h2 cb bd16","&Cross;"] },
			{ s:["d x t08 cb tc","Close"] },
			{ div:["e"] }
		]},
		
		{ div:["d w09 gnws x call_hangup_"], c:
		[
			{ ac:["c ao","","_hangup","x t b03 w02 h02 h2 ma bd16 gb cw tc",""], c:
			[
				{ s:["","&Cross;"] },
				{ div:["e"] }
			]},
			{ s:["c x s cb t tc","Hangup"] },
			{ div:["e"] }
		]}, 
			
		{ div:["d w09 gnws x"], c:
		[
			{ div:["c"], c:
			[
				{ ac:["ao call_connected_","call_add_form_main-r_","_add_dial_form","x t b03 w02 h02 h2 ma bd16 gb cw tc",""], c:
				[
					{ s:["","+"] },
					{ div:["e"], c:[ { arg:["_uid","",":v:activities:src_uid"] } ] }
				]},
				{ div:[] }
			]},
			{ s:["c call_connected_ x t s cb tc","Add"] },
			{ s:["c call_connected__ x y w02 ma bd16 cd_ tc h2","+"] },
			{ s:["c call_connected__ x t s cd_ tc","Add"] },
			{ div:["e"] }
		]},
		{ div:["d w09 gnws x"], c:
		[
			{ input:["g","chanholdstate","","1","checkbox"] },
			{ div:["w10 btnhold"], c:
			[
				{ ac:["c ao call_connected_","","_hold","x y w02 h2 ma bd16 gb cw tc","||"] },
				{ div:["c call_connected_"], s:["x y s cb btnhold_lbl","Hold"] },
				{ div:["c call_connected_"], s:["x y s cr btnunhold_lbl","UnHold"] },
				{ s:["c call_connected__ x y w02 ma bd16 cd_ tc h2","||"] },
				{ s:["c call_connected__ x y s cd_ btnhold_lbl","Hold"] },
				{ div:["e"] }
			]}
		]},
		
		{ div:["d w09 call_connected_"], c: 
		[
			{ div:["g"], c: // show only in cbid
			[
				{ ac:["c ao","","_answer","x t b03 w02 h02 h2 ma cb tc micon","group"] },
				{ s:["c t08 cb","4"] },
				{ div:["e"] }
			]}
		]},
			
		{ div:["d w09 gnws"], s:[":v:activities:src_vector::vector:7",""], c:
		[ 
			{ div:["w09 x ao call_ringing_"], c:
			[
				{ ac:["c ","","_answer","x t b03 w02 h02 h2 ma bd16 gb cw tc micon","call"] },
				{ s:["c x t s cb tc","Answer"] },
				{ div:["e"] }
			]} 
		]},
				
		{ div:["e"] }
	]}
]};

//te["call_toolbar"] = { div:["ma w14",":v:activities:src_uid"], c: //  
//[
//	{ input:["g","","sbl","100","radio","1"] },
//	{ ac:["abs mtn37 ao w14 sbl","","_activity_show","w13 x bd cb gws_",""], c:[ { div:[""], c:
//	[
//		{ s:["c w07 l y",""] },
//		{ s:["d w05 r05 y tr",""] },
//		{ arg:["ts","",""] }, 
//		{ div:["e"] }
//	]} ]},
//]};

te["call_toolbar"] = { div:["ma w20",":v:activities:src_uid"], c: //  
[
	{ input:["g","ati_toolbar","barr","1","radio","1"] },
	{ li:["abs mtn37 ao w20 bd"], ev:["_activity_show"], s:["w20 bd cw",""], c:[ { div:["gr"], c:
	[
		{ s:["c x y ",":v:activities:src_address"] },
		{ s:["c x y ",""] },
		{ s:["d xx y ",""] },
		{ arg:["ts","",":v:activities:src_ts"] }, 
		{ div:["e"] }
	]} ]},
]};

te["call_ringing"] = { div:["w45ma bd sh__ gw xx yy","vddvw"], ev:["_undd"], c:
[
	{ div:["g"], c:
	[
		{ ac:["d ay","","_vpclose","x y bd_ h2 cb","&Cross;"] },
		{ div:["e"] }
	]},
	{ div:["tt"], s:["w12 ma",""], c:[ { img:["","","/helpline/images/Icon_Call.png","120"] } ] },
	{ s:["yy tc n co ","::vector:14:9"] },
	{ s:["yy tc h2 ","%12"] },
	// list possible contact -- not action 
	// Answer button
]};

// --------------------------------------------------------------------
				
te["chan_args"] = { p:["",":V:ami:CHAN_UNIQUEID"], c:
[
	{ arg:["","src_state",""] },
	{ arg:["","src_state_ts",""] },
	{ arg:["","src_state_ts_txt",""] },
	
	{ arg:["","cbid",":V:ami:CHAN_EXTEN_MASQ"] }, // confbridgeid
	{ arg:["","chan2",":V:ami:CHAN_CHAN_2"] },
	{ arg:["","phone",":V:ami:CHAN_CID_NUM_2"] }, // phone = cid2
	{ arg:["","src_orig",":V:ami:CHAN_ORIG"] },
				
	{ arg:["","src","call"] },
	{ arg:["","src_ts",":V:ami:CHAN_TS"] },
	{ arg:["","src_uid",":V:ami:CHAN_UNIQUEID"] },
	{ arg:["","src_action_id",":V:ami:CHAN_ACTION_ID"] },
	{ arg:["","src_campaign_id",":V:ami:CHAN_CAMPAIGN_ID"] },   
	
	{ arg:["","chan",":V:ami:CHAN_CHAN"] },
	{ arg:["","usr",":V:ami:CHAN_CALLERID_NUM"] },
	{ arg:["","_cid_name",":V:ami:CHAN_CALLERID_NAME"] },
	{ arg:["","callid",":V:ami:CHAN_SIPCALLID"] },
	{ arg:["","vector",":V:ami:CHAN_VECTOR"] },
	{ arg:["","src_uid2",":V:ami:CHAN_UNIQUEID_2"] },
]};
				
te["chan_add"] = { p:["","%2"], s:["",""], c:
[
	{ input:["g","optc_add","chvw0","%2","radio",""] }, 
	{ div:["x y gw"], c: 
	[
		{ s:["c x t cb b",""] },	// cid_num
		{ s:["c x t cb",""] },		// cid_name
		{ s:["c x t g",""] },		// vector
		{ s:["c x t g",""] },		// cid2
		{ s:["d x t",""] },		// status-duration
		{ arg:["ts","",""] }, 		// status-ts
		{ s:["d x t",""] }, 		// status-text
		{ div:["e"], c:[ { arg:["","chan3","%3"] }, { arg:["","exten","%4"] }, { arg:["","chan_ts","%1"] }, { arg:["","cid","%4"] }, { arg:["","ctx",":V:ami:CHAN_CONTEXT_MASQ"] } ] }
	]},
	{ div:["t","ve"] }
]};

te["chan_call"] = { p:["ba mtn1","%2"], c:[ { li:[""], ev:[], c: 
[ 
	{ input:["g","optc","chvw0","%2","radio",""] }, 
	{ div:["x y02 gw "], c:
	[
		{ s:["c w11 x y",""] },	// cid_num
		{ s:["c x y cb",""] },		// cid_name
		{ s:["c w02 x y",""] },	// vector
		{ s:["c x y s",""] },		// cid2
		{ s:["d x y w08 tr",""] },		// status-duration
		{ arg:["ts","",""] }, 		// status-ts
		{ s:["d x y w08 tr s",""] }, 		// status-text
		{ div:["e"] }
	]},
	{ div:[] }
]} ]};

te["chan_agent_sup"] = { c:
[
	{ div:["ab","va"], ac:["content-hidden","","_dd","cb",""], c:
	[
		{ s:["content-shown_ w02 y gd cw tc micon","more_vert"] }, 
		{ s:["content-hidden_ w02 y tc micon","more_vert"] }, 
	]},
	{ div:["dd w12 y gd cw mln10","vdd"], ev:["_undd"], c:
	[
		{ div:[], c:
		[
			{ input:["g","optsupc","optsupc","2","radio"] },
			{ ac:["tabi_ ay","","_sup","xx y cw","Spy"], c:[ { arg:["","action","2"] }, { arg:["","exten","%0"] } ] },
			{ div:[] }
		]},
		{ div:[], c:
		[
			{ input:["g","optsupc","optsupc","3","radio"] },
			{ ac:["tabi_ ay","","_sup","xx y cw","Whisper"], c:[ { arg:["","action","3"] }, { arg:["","exten","%0"] } ] },
			{ div:[] }
		]},
		{ div:[], c:
		[
			{ input:["g","optsupc","optsupc","4","radio"] },
			{ ac:["tabi_ ay","","_sup","xx y cw","Barge"], c:[ { arg:["","action","4"] }, { arg:["","exten","%0"] } ] },
			{ div:[] }
		]},
		{ div:[], c:
		[
			{ input:["g","optsupc","optsupc","9","radio"] },
			{ ac:["tabi_ ay","","_sup","xx y cw","Force Logout"], c:[ { arg:["","action","9"] }, { arg:["","exten","%0"] } ] },
			{ div:[] }
		]}
	]}        	
]};

te["chan_sup"] = { p:["","%2"], c:[ { div:[""], c:
[
	{ s:["c xx y h02 gr cw",":V:ami:CHAN_CONTEXT_MASQ"] },
	{ s:["c xx y h02 gr cw","0:00"] },			// status-duration
	{ arg:["ts","",":V:ami:CHAN_PROMPT_TS0"] }, 	//
	{ div:["c"], c:
	[
		{ input:["g","optsupc","optsupc","0","radio"] },
		{ ac:["tabi_ ab","","_sup","x07 y h02 gr cw h3","&Cross;"], c:[ { arg:["","action","0"] } ] },
		{ div:[] }
	]}, 
	{ div:["e"] }
]} ]};

te["chan_agent_cid_name"] = { s:["","%1"] };

te["chan_agent"] = { p:["","%2"], c:[ { div:[], c:
[
        { input:["g","optc","chvw0","%2","radio",""] },
        { li:["y02 gws_ mtn1"], c: // x y02 gw bl_ br_ bb_
        [
                { s:["c w03 ll y cb",""] },      // cid_num
                { s:["c w08 x y cb",null] },    // cid_name
                { s:["c w02 x y cb",""] },      // vector
                { s:["c w12 x y s",""] },   	// cid2
		{ div:[] },

		{ div:["d l "], c:
		[
			{ div:["admin_"], chan_agent_sup:[] },
			{ div:["supervisor_"], chan_agent_sup:[] }
		]},

                { s:["d x y w08 tr b",""] },    // status-duration
                { arg:["ts","",""] },           // status-ts
                { s:["d x y w08 tr s",""] },    // status-text
                           
                { div:["e"] }
        ]},
        { div:["mb"] }
]} ]};

te["aa_status"] = { div:["",null], c:[ { div:["","ve"], c:
[
	{ div:["b05 btn"], c:
	[
		{ input:["g","is_auto_answer","","1","checkbox",null] },
		{ ac:["r ay w21","agent-agent","_postjb","h01_ xx y07 cb",""], c:
		[ 
			{ div:["c t02 w01_"], s:["chk",""] },
			{ s:["c x h02","Auto Answer "] },
			{ p:["e","o"], arg:["","action",null] }
		]},
	]},
	{ s:["x y go cw savl","..."] }
]} ]};


te["joinq_status"] = { div:["",null], c:[ { div:["","ve"], c: // 
[
	{ ac:["btn aa","agent-agent","_postjb","xx y cb ",""], c:
	[
		{ s:["",null] },
		{ p:["","o"], c:[ { arg:["","action",null] }, { arg:["",null,null] }  ] } 
	]},
	{ s:["x y go cw savl","..."] }
]} ]};

te["agent_status"] = { div:["y02",null], c: 
[
	{ div:["c xx t08"], s:[null,""] },
	{ div:["c y"], s:[null,null] },
	{ s:["d r10 y cb tr",null] },		// status-duration
	{ arg:["ts","",null] }, 		// status-ts
	{ div:["e"] },
]};

// -------------------------------------------------------

function _sup ()
{
	this.previousSibling.checked = true;
	var o = {};
	argv (this, o);
	url (this.nextSibling, "sup", "sup", "", null, 2, o, "POST");
}

// -------------------------------------------------------

function users_online_ufn (el, u, a, r, m)
{
	var kk = Object.keys (re["peers"]);
	var v = "";
	for (var k=0; k<kk.length; k++)
	{
		if (k>0) v+=",";
		v+=kk[k];
	}
	el.lastChild.value = v;
}

function call_popup_end (ts)
{
	var coll = document.getElementById ("vv").childNodes;
			
	// notif --> closed by phone.js (after this function return)
	
	// toolbar
	var coll_ = coll[1].firstChild.childNodes[1].firstChild.firstChild.childNodes;
	coll_[0].parentNode.className = "cr b gp";
	coll_[0].innerHTML = "Wrapup";
	coll_[1].innerHTML = hmst ((ts*1), ["","","","","","",""]); // status-duration;
	coll_[2].value = ts; // dont stop timer
	
	// action btns
	var p = _(coll[6].childNodes[1].childNodes[1].firstChild,"src_btns")
	var last_status = p.firstChild.childNodes[1].className;
	p.firstChild.childNodes[1].className = "call_ended";
	if (last_status!="call_connected")  // auto close popup is call not connected
	{
		activity_close (); // clear
	}	
}

function call_popup_hold_state (el, f)
{
	var p = _(document.getElementById ("vv").childNodes[6].childNodes[1].childNodes[1].firstChild,"src_btns")
	var a = {};
	argv (el, a);
	console.log ("call_popup_hold_state ("+f+") "+p.id+"=="+a.src_uid)
	if (p.firstChild.id!=a.src_uid) return;
	var el_ = _(p.firstChild, "chanholdstate", "input");
	if (el_) el_.checked = f;
}

function call_popup_upd (el)
{
	var coll = document.getElementById ("vv").childNodes;	
	var ss = [
	["Down","call_ringing","gr cw"],
	["Dialing","call_ringing","gr cw"],
	["Ringing","call_ringing","gr cw"],
	["Waiting","call_connected","gr cw"],
	["Waiting","call_connected","gr cw"],
	["Connected","call_connected","gg cw"],
	["Call Ended","call_ended","cb"],
	["On Mute","call_connected","gr cw"],
	["On Hold","call_connected","gr cw"]];
	var p = __(el,"va");
	var vs = CALLS[p.previousSibling.value];
	var a = {};
	argv (p, a);
	if (vs && vs.ishold==true) { a.src_state = 8; a.src_state_ts = vs.ishold_ts; }
	var ts_txt = hmst (a.src_state_ts, ["","","hms","","","",""]); // a.src_state_ts_txt;
	
	// notif (sbr)
	var coll_ = el.parentNode.parentNode.childNodes[0].childNodes;
	coll_[1].innerHTML = ts_txt;
	coll_[2].value = a.src_state_ts;
	el.parentNode.parentNode.childNodes[1].childNodes[2].innerHTML = ss[a.src_state][0];
	
	// toolbar
	if (coll[1].childNodes.length<1) return -1;
	if (coll[1].firstChild.id.length<1) return -2;
	if (coll[1].firstChild.id!=a.src_uid) return -3;
	
	coll_ = coll[1].firstChild.childNodes[1].firstChild.firstChild.childNodes;
	//coll_[0].parentNode.className = ss[a.src_state][2];
	coll_[0].innerHTML = ss[a.src_state][0];
	coll_[1].innerHTML = ts_txt;
	coll_[2].value = a.src_state_ts;
		
	// action btns
	_(coll[6].childNodes[1].childNodes[1].firstChild,"src_btns").firstChild.childNodes[1].className = ss[a.src_state][1];
	
	return 0;	
}

function call_popup (el, f=0)
{
	var coll = document.getElementById ("vv").childNodes;
	var r_ = re["r_"][0].slice(0);
	var a = {};
	var k = re["activities_k"]
	var el_ = __(el,"va");
	
	// todo: show answer call popup
	
	if (f==0 && coll[1].childNodes.length>0 && coll[1].firstChild.id.length>0) // vw is occupied
	{
		argv (el_, a);
		console.error ("[popn] "+coll[1].firstChild.id+","+a.src_uid+" | "+el_.previousSibling.value)
		// notify (el); // create transient notification 
		return
	}

	ra = {};
	for (var k_ in re) ra[k_]=re[k_];		
	argv (el_, a);
	r_[k["src"][0]] = "call";
	r_[k["src_uid"][0]] = a.src_uid;
	r_[k["src_address"][0]] = _phone_fmt (a.src_address);
	r_[k["src_uid2"][0]] = a.src_uid2;
	r_[k["src_usr"][0]] = a.usr;
	r_[k["src_vector"][0]] = a.src_vector;
	r_[k["src_callid"][0]] = el_.previousSibling.value;
	r_[k["src_ts"][0]] = a.src_ts;
		
	console.log ("call_popup args:"+JSON.stringify (a)+"|"+JSON.stringify (r_));
	
	if (a.cid_name=="AgentLogin" || a.cid_name=="Supervisor") return;
	
	// todo: get current checkted tab in coll[6]
	
	el_.previousSibling.checked = true; 	// hilite call-notif
	coll[1].innerHTML = ""; 			
	coll[6].childNodes[1].firstChild.checked = true;
	coll[6].childNodes[1].childNodes[1].innerHTML = "";

	var s = "-1?src=" + a.src + "&src_uid=" + a.src_uid; 
	if (r_[k["src_address"][0]].length>0)  
	{
		s += "&src_address="+r_[k["src_address"][0]];
	}

	nd (coll[1], te["call_toolbar"], [], r_, [0]); // show toolbar	
	nd (coll[6].childNodes[1].childNodes[1], te["activity_vw_id"], ["call_btns","","1"], r_, [3]);	
	url (coll[6].childNodes[1].childNodes[1].lastChild, "activity_vw_id_match", "activities", s);

	var isaa = document.getElementById ("is_auto_answer");
	var sess = CALLS[r_[k["src_callid"][0]]];
	if (a.src_vector=="2" && isaa.checked==true && a.src_address.length>3)
	{
		console.log ("AUTO ANSWER "+a.src_address+"|"+r_[k["src_callid"][0]])
		if (sess && sess.session) sess.session.accept ({ sessionDescriptionHandlerOptions: { constraints: { audio: true, video: false } } });
	}
}

function _call_popup () 
{
	call_popup (this.childNodes[1].lastChild.firstChild, 1); 
	call_popup_upd (this.childNodes[1].lastChild.firstChild); 
	var vs = CALLS[this.previousSibling.value]
	if (vs && vs.ishold) call_popup_hold_state (this.parentNode, vs.ishold); // load hold state
}

// ------------------------------------------

function ch_status (ch)
{
	var st = 10;
	ch[10] = ch[1];
	for (var i=10; i<19; i++) 
	{
		if (ch[i].length<1) continue; 
		st = i;
		if (i==AMI.CHAN_STATE_HANGUP) break; // chan hangup
	}
	return st;
}

function chan_status (tp, ch) 
{
	var ss = 
	{
		"chan_args":["Down","Dialing","Ringing","Available","Waiting","OnCall","Call Ended","On Mute","On Hold"],
		"chan_agent_start":["Down","Dialing","Ringing","Waiting","Dialing...","OnCall","Call Ended","On Mute","On Hold"],
		"chan_agent":["Down","Dialing","Ringing","Available","Ringing","OnCall","CallEnded","Wrapup","OnHold"],
		"chan_call":["Down","Dialing","Ringing","IVR","In Queue","Connected","Call Ended","On Mute","On Hold"],
		"chan_add":["Down","Dialing","Ringing","IVR","In Queue","Connected","Call Ended","On Mute","On Hold"],
	};
	var st = ch_status (ch);
	ch[AMI.CHAN_STATUS_] = ""+(st-10); 				// status id
	ch[AMI.CHAN_STATUS_TXT_] = ss[tp][(st-10)];			// status txt
	ch[AMI.CHAN_STATUS_TS_] = ch[st];					// status-ts
	ch[AMI.CHAN_STATUS_TS_TXT_] = hmst (ch[st], ["","h","hms","0",""]);	// status-duration
	var ch2 = null;
	if (ch[AMI.CHAN_UNIQUEID_2].length>0) ch2 = re["channels"][ch[AMI.CHAN_UNIQUEID_2]];
	if (ch2!=null && ch[AMI.CHAN_ORIG].length>0 && ch[AMI.CHAN_VECTOR]!="2") // use status of peer when autodialing
	{
		var st2 = ch_status (ch2);
		ch[AMI.CHAN_STATUS_] = ""+(st2-10); 				// status id
		ch[AMI.CHAN_STATUS_TXT_] = ss["chan_call"][(st2-10)];			// status txt
		ch[AMI.CHAN_STATUS_TS_] = ch2[st2];					// status-ts
		//ch[AMI.CHAN_STATUS_TS_TXT_] = hmst (ch2[st2], ["","h","hms","0",""]);	// status-duration
	}
}

function chani (tp,p,ch,ts,k_=2,top_=0)
{
	// console.log ("[chani]"+p.id+"|"+ch[2])
	var mm = 
	{ 
		"chan_agent_start":[[1,0],[-1,-1],[1,3],[1,4], [2,5],[1,1]],
		"chan_agent":[[1,AMI.CHAN_CALLERID_NUM], [-1,-1], [1,-1], [1,AMI.CHAN_CID_NUM_2], [-1,-1], [-1,-1], [1,AMI.CHAN_STATUS_TS_TXT_], [2,AMI.CHAN_STATUS_TS_], [1,AMI.CHAN_STATUS_TXT_] ],
		"chan_call":[[1,AMI.CHAN_CID_NUM_2], [-1,-1],  [1,AMI.CHAN_VECTOR,"::vector:0:5"], [1,AMI.CHAN_CALLERID_NUM], [1,AMI.CHAN_STATUS_TS_TXT_],[2,AMI.CHAN_STATUS_TS_],[1,AMI.CHAN_STATUS_TXT_]],
		"chan_add":[[1,AMI.CHAN_CALLERID_NUM],[-1,-1],[-1,-1], [1,AMI.CHAN_CID_NUM_2], [1,AMI.CHAN_STATUS_TS_TXT_],[2,AMI.CHAN_STATUS_TS_],[1,AMI.CHAN_STATUS_TXT_]],
	};
	var status = ["co","cr","cr","cd","cr","cg","cr","co","gp cr"];
	var atr = ["cr","innerHTML","value"];
	var m = mm[tp];
	var el = _(p,ch[k_]);
	if (el==null && tp==null) return null;
	
	if (el==null)
	{
		var a_ = [];
		if (tp=="chan_agent") { a_=[""]; } // { a_=[p.nextSibling.value]; }
		el = nd (p, te[tp], a_, ch, [a_.length]);
		el = el.parentNode.parentNode;
		chan_a[ch[2]] = { "el":el, "ts":ts }; // append chan to chan_a index
		if (tp=="chan_agent") // query usr details
		{
			console.log ("-------------chan_agent")
			url (el.firstChild.childNodes[1].childNodes[1], "chan_agent_cid_name", "wallonly", ("?exten="+ch[AMI.CHAN_CALLERID_NUM]+"&_c=1"));
		}
	}
	chan_a[ch[2]].ts=ts;
	chan_status (tp, ch);
	var coll = el.firstChild.childNodes[1].childNodes; 
	var v = "";
	for (var j=0; j<m.length; j++)
	{
		if (m[j][0]<0) continue;
		v = "";
		if (m[j][1]>-1) v = ch[m[j][1]];
		if (m[j].length>2) v = valf ([v], m[j][2]);
		coll[j][atr[m[j][0]]] = v;
	}
	el.firstChild.className = status[ch[AMI.CHAN_STATUS_]];
	return el;
}

function chan_sup (pa,ch,ts)
{
	var el = _(pa, ch[AMI.CHAN_UNIQUEID]); // find sup chan	
	var el_ = _(pa, ch[AMI.CHAN_EXTEN_MASQ]); // find agent chan
	if (el_==null) return;
	if (el && el.parentNode.parentNode.id!=ch[AMI.CHAN_EXTEN_MASQ]) // delete 
	{
		var p = el.parentNode;
		p.removeChild (el);
		el = null;
	}
	if (el==null)
	{
		el_.firstChild.lastChild.innerHTML = "";
		el = nd (el_.firstChild.lastChild, te["chan_sup"], [], ch, [0]);
		el = el.parentNode.parentNode;
		chan_a[ch[2]] = { "el":el, "ts":ts }; // append chan to chan_a index
	}
	var coll = el.firstChild.childNodes;
	coll[0].innerHTML = ch[AMI.CHAN_CONTEXT_MASQ];
	coll[1].innerHTML = hmst (ch[AMI.CHAN_PROMPT_TS0], ["","h","hms","0",""]);	// status-duration
	coll[2].value = ch[AMI.CHAN_PROMPT_TS0];
}

function chans_pop (ts)
{		
	var h=0, n=0, trunk=0;
	var k = Object.keys (chan_a);
	for (var i=0; i<k.length; i++)  // remove closed, hangup channels
	{
		var id = k[i];
		if (chan_a[id].ts==ts) continue;
		console.log ("[pop] "+id+" "+chan_a[id].el +" | "+ts)
		if (chan_a[id].el && chan_a[id].el.parentNode) 
		{
			var pe = chan_a[id].el.parentNode;
			var el = chan_a[id].el;
			var a = {};
			argv (el, a);
			var el_removed = pe.removeChild (chan_a[id].el); 
	
			if (pe.id=="vinbound") trunk++;

			if (pe.id=="cba")
			{
				console.log ("pop cba removed | "+pe.previousSibling.id+" | "+el_removed)
				var ch = re["channels"][pe.previousSibling.id];
				if (ch && el_removed) { nd (pe, te["call_add_ld"], [], [a.chan_ts, ch[AMI.CHAN_CBO], a.cid], [0]); }
			}
		}
		delete chan_a[id];
		h++;
	}
	if (trunk>0)
	{
		var p_ = document.getElementById ("wall_rpt_call");
		console.log ("Refresh inbound stats stats | "+p_);
		// rpt (p_.childNodes[1]);
	}
	return h;
}

function chan_add (vp_add, ch, ch_, ts)
{
	var m_ = 0;

	if (ch_ && ch_[AMI.CHAN_STATE_HANGUP].length>0) ch_=null;
								
	if (vp_add.firstChild.firstChild.id=="add_ld")  // show cbo status b4 chan_add is created
	{
		var coll_ = vp_add.firstChild.firstChild.childNodes[1].childNodes;
		var action_ts = coll_[2].value*1; // todo: adjust for time diff between asterisk and app servers			
		console.log ("[add_ld] <"+ch[AMI.CHAN_CBO]+"> "+action_ts +" "+ch[AMI.CHAN_CBO_TS]);
		if (action_ts < (ch[AMI.CHAN_CBO_TS]*1))
		{
			var st_ = re["chan_action"][ch[AMI.CHAN_CBO]];
			coll_[0].innerHTML = "";
			coll_[2].id = st_?st_[3]:"";
			nd (coll_[0], te["call_add_msg"], [], [ch[AMI.CHAN_CBO]], [0]);
		}
		m_++;
	}
				
	if (ch_ && (vp_add.firstChild.firstChild.id.substr(0,4)=="add_" || ch_[AMI.CHAN_XFER]=="obc"))
	{
		console.log ("[chan_add] "+ch_[AMI.CHAN_XFER]+" | "+vp_add.nextSibling.id);
		if (vp_add.firstChild.firstChild.id=="add_ld") vp_add.firstChild.innerHTML="<div id='add_ing'></div>"; 
		var el_ = chani ("chan_add", vp_add.nextSibling, ch_, ts, 2, 1); 
		if (ch_[AMI.CHAN_XFER]=="obc" && el_.firstChild.lastChild.childNodes.length==0) // set oly during create
		{
			nd (el_.firstChild.lastChild, te["chan_add_btns"], [], ch_, [0]);
			m_++;
		}
		if (ch_[AMI.CHAN_XFER]!="obc")
		{ 
			r_ = [ch_[1], ch_[AMI.CHAN_XFER]]; 
			el_.firstChild.lastChild.innerHTML = "";
			nd (el_.firstChild.lastChild, te["chan_add_done"], [], r_, [0]);
			m_++;
		}
	}
				
	if (m_==0 && vp_add.firstChild.id!="ve" && vp_add.nextSibling.childNodes.length==0) // show form
	{
		vp_add.innerHTML = "";
		nd (vp_add, te["call_add_form"], [], ch, [0]);
	}			
	
	console.log ("[vp_add:"+ch[AMI.CHAN_EXTEN_MASQ]+"] ("+ch[AMI.CHAN_CBO]+","+ch[AMI.CHAN_CBO_TS]+","+ ch[AMI.CHAN_CBO_UNIQUEID]+")  => ("+(ch_?ch_[AMI.CHAN_XFER] : "") + ")");
}

function chans (o,k,ts)
{
	var pa = document.getElementById ("vagents");
	var pq = document.getElementById ("vqueued");
	var pi = document.getElementById ("vinbound");
	var po = document.getElementById ("voutbound");
	var ps = document.getElementById ("vstats");
	var pu = document.getElementById ("call_sessions");
	var user_cid = document.getElementById ("user_cid").value;
	var vp_add = null
	var vp_members = null;
	var ch_agent = null;
	var is_trunk = 0;
	var c = [0,0,0,0,0,0,0];
	var cn = ["","","",""];
	
	var pvp = document.getElementById ("vp");
	if (pvp && pvp.firstChild && pvp.firstChild.firstChild)
	{
		if (pvp.firstChild.firstChild.id=="vp_add") vp_add = pvp.firstChild.childNodes[1];
		if (pvp.firstChild.firstChild.id=="vp_members") vp_members = pvp.firstChild;
	}
	
	//console.log ("[ldami] "+JSON.stringify (k)+ " | "+ts)
	//console.log (o)
	                
	// k.sort ();
	for (var i=k.length-1; i>-1; i--)
	{
		var ch = o[k[i]];
		
		if (!ch) { console.log ("[undefined chan] "+i+": "+k[i]); continue; }	
		if (ch[AMI.CHAN_STATE_HANGUP].length>0) continue; // skip hangup'ed channels
		// if (ch[AMI.CHAN_SIPCALLID].length<1) continue; // skip setup channels --skips agent chan

		if (ch[AMI.CHAN_CONTEXT_MASQ]=="start-agent-login")
		{
			// chani ("chan_agent_start", pa, ch, ts); 
			// todo: user: // if (user_cid.length>0 && user_cid==chan[4]) fn()
			// continue;
		}

		if (ch[0].length>0) 		 // agent session chan
		{
			c[0]++; 
			if (user_cid.length>0 && user_cid==ch[0]) ch_agent = ch;
			var el_ = chani ("chan_agent", pa, ch, ts);
			if (ch[AMI.CHAN_UNIQUEID_2].length>0 && o[ch[AMI.CHAN_UNIQUEID_2]]) el_.firstChild.childNodes[1].childNodes[2].innerHTML = re['vector'][o[ch[AMI.CHAN_UNIQUEID_2]][AMI.CHAN_VECTOR]][2];
			continue;
		}

		if (ch[6].substr(0,4)=="DLPN" && ch[AMI.CHAN_SIPCALLID].length>0 && (ch[3].substr(6,4)==(user_cid+"-") || ch[3].substr(6,5)==("0"+user_cid+"-")))  
		{		
			var el = _(pu, ch[2]); // find matching call	
			
			if (el==null)
			{
				var el_ = _(pu, ch[AMI.CHAN_SIPCALLID].substr (0,20));
				if (el_)
				{
					nd (el_.childNodes[1].childNodes[1].lastChild, te["chan_args"], [], ch, [0]);
					el = el_.childNodes[1].childNodes[1].lastChild.firstChild;
					if (!chan_a[ch[2]]) chan_a[ch[2]] = { "ts":ts };
					// console.log (ch);		
					call_popup (el);
				}
			}
			
			if (el) 
			{
				//console.log ("chan-usr "+ch[2]+" | "+ch[6])
				chan_a[ch[2]].ts=ts;
				chan_status ("chan_args", ch);
				el.childNodes[0].value = ch[AMI.CHAN_STATUS_]; // status code
				el.childNodes[1].value = ch[AMI.CHAN_STATUS_TS_];  // status ts
				el.childNodes[2].value = ch[AMI.CHAN_STATUS_TS_TXT_];  // status ts txt
				el.childNodes[3].value = ch[AMI.CHAN_EXTEN_MASQ]; // update exten_masq
				el.childNodes[4].value = ch[AMI.CHAN_CHAN_2]; // update last peer chan
				el.childNodes[5].value = ch[AMI.CHAN_CID_NUM_2]; // update last peer cid
				el.childNodes[6].value = ch[AMI.CHAN_ORIG]; // autodial status
				call_popup_upd (el);
						
				if (vp_add && vp_add.id==ch[AMI.CHAN_UNIQUEID]) 
				{
					chan_add (vp_add, ch, o[ch[AMI.CHAN_CBO_UNIQUEID]], ts);
				}
			}
			
			if (ch[AMI.CHAN_CONTEXT_MASQ].substr (0,11)=="supervisor_") // my supervising chan
			{
				chan_sup (pa, ch, ts)
			}

			continue;
		}
		
		//if (vw_activity && vw_activity.id==ch[AMI.CHAN_EXTEN_MASQ]) // list cb members for current activty
		{
			// count active channels linked to current vw
			
			// if (vp_members) // show in vp
			{
			
			}
		}

		is_trunk=0;
		if (ch[AMI.CHAN_CONTEXT].substr (0,5)=="trunk") is_trunk=1;
		if (ch[AMI.CHAN_CONTEXT_MASQ].substr (0,5)=="trunk") is_trunk=1; // debug
		
		if (is_trunk && ch[AMI.CHAN_EXTEN]!="s") // inbound
		{
		
			// console.log ("[inbound] "+ch[AMI.CHAN_CONTEXT_MASQ])
		
			if (ch[AMI.CHAN_STATE_QUEUE].length>0 && ch[AMI.CHAN_STATE_CONNECT].length==0) 		// inbound waiting
			{
				c[1]++; 				// waiting count
				c[2]+= (ts-ch[AMI.CHAN_STATE_QUEUE]);	// wait-time total
				if (ch[AMI.CHAN_STATE_QUEUE]<c[3] || c[3]==0) c[3]=ch[AMI.CHAN_STATE_QUEUE]; // wait-time max
			}
			if (ch[AMI.CHAN_STATE_QUEUE].length>0 && ch[AMI.CHAN_STATE_CONNECT].length>0)
			{
				c[4]++; 		// inbound connected
				// todo: remove from inbound
			}
			c[5]++; 
			chani ("chan_call", pi, ch, ts); 
			continue;
		}
		
		if (is_trunk && ch[AMI.CHAN_EXTEN]=="s") // outbound
		{
			c[6]++; 
			chani ("chan_call", po, ch, ts); 
			continue;
		}
	}

	var p_agent = document.getElementById ("agent_status");
	var p_joinq = document.getElementById ("joinq_status");
	var p_aa = document.getElementById ("aa_status");
	var a_ = [];
	var a__ = [];
	var status_ = ["go","go","go","gg","go","gg","gr","go","gr"];

	a_= ["","","On Break","cb","w01 h01 bd go","aonbreak"];
	a__ = ["","","1","Join Queue","outjoinq"];
	cn_ = document.getElementById("vv").className;
	if (cn_!="counsellor" && cn_!="supervisor" && cn_!="media") { a_[2]="My Account";  a_[4]=""; } // non agent
	if (ch_agent!=null) 
	{ 
		a_ = [ch_agent[AMI.CHAN_STATUS_TS_], ch_agent[AMI.CHAN_STATUS_TS_TXT_], ch_agent[AMI.CHAN_STATUS_TXT_], "cb", ("w01 h01 bd "+status_[ch_agent[AMI.CHAN_STATUS_]]), ("a"+ch_agent[AMI.CHAN_STATUS_TXT_]).replace (" ","_")]
		// console.log ("AGENT_STATUS: "+ch_agent[AMI.CHAN_STATUS_]+":"+ch_agent[AMI.CHAN_STATUS_TXT_]);
		a__ = ["coffee","break","0","Leave Queue","injoinq"]
	} 
	console.log ("-----cti:"+a_[5]);
	if (p_agent && p_agent.firstChild.id!=a_[5]) 
	{
		p_agent.innerHTML = "";
		p_joinq.innerHTML = "";
		nd (p_agent, te["agent_status"], a_, [], [6]);
		nd (p_joinq, te["joinq_status"], a__, [], [5]);
	}

	a_ = ["z","","aa_none"];
	if (ch_agent!=null)
	{
		a_ = ["4","","aa_off"];
		if (ch_agent[AMI.CHAN_CAMPAIGN_WRAPUP]=="INUSE") a_ = ["5","1","aa_on"];
	}
	if (p_aa && p_aa.firstChild.id!=a_[2]) 
	{		
		p_aa.innerHTML = "";
		nd (p_aa, te["aa_status"], a_, [], [3]);
	}

	pa.parentNode.firstChild.childNodes[1].innerHTML = c[0];      // agent count
        pi.previousSibling.childNodes[1].innerHTML = c[5];      // inbound count
        var cnk = "c x y";
        var cnv = "d xx y";
        if (c[1]>0) { cnk = "c x y cr"; cnv="d xx y gr cw bd16";  }
        pq.previousSibling.childNodes[0].className = cnk;
        pq.previousSibling.childNodes[1].className = cnv;
        pq.previousSibling.childNodes[1].innerHTML = c[1];      // waiting

}

function ldami (o,c)
{
        var ts = (Date.now ()/1000);
        var k = Object.keys (o);
        re["channels"] = o;
        chans (o, k, ts);
        chans_pop (ts);
}

