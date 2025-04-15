
te["call_session"] = { /*p:["","sipid(0,10)"],*/ c: 
[ 
	{ input:["g","","sbl","%0","radio"] }, // sipid js full
	{ li:["sbr x15 y","va"], ev:["_call_popup"], c:  
	[ 
		{ div:["abs w02_ y g"],  c:
		[ 
			{ s:["c cr h3 micon","phone_in_talk"] },
			{ p:["e","o"], c:[ { arg:["","src_address",":v:activities:src_address"] }, { arg:["","src_usr",":v:activities:src_usr"] }, { arg:["","src_vector",":v:activities:src_vector"] }, { arg:["","cid_name","%1"] } ] }
		]},
		{ div:["ml4nn s"], c:
		[					
			{ div:[], c: 
			[
				{ s:["c x y",":v:activities:src_vector::vector:4"] },
				{ s:["d x y","0:00"] },
				{ arg:["ts","",":v:activities:src_status"] }, 		// status-ts
				{ div:["e"] }
			]},
			
			{ div:[], c:
			[
				{ s:["c x y02",":v:activities:src_address"] }, // phone
				{ s:["c x y02 n",":v:activities:src_vector::vector:5"] },
				{ s:["d x y02 gr cw bd","..."] }, // status
				{ div:["e"] }
			]},
		
			{ div:["g x tt"], u:[null] },  // session-buttons: hold, hangup
			
			{ div:["g x","va"] },  // cti-buttons (on connect)
			{ p:["xx","add"] }, // added chans
		
			{ p:["g"], uaudio:[null,"",""] },
			{ p:["","o"] } // this channel args from ami
		]},
		{ div:[] }
	]} 
]};

// -----------------------------

function DetectDevices()
{
    	if (!navigator.mediaDevices) { console.log ("VOICEAPPS: navigator.mediaDevices Failed!");  return; }
    	navigator.mediaDevices.enumerateDevices().then ( function (dev) 
    	{
        	// deviceInfos will not have a populated lable unless to accept the permission
        	// during getUserMedia. This normally happens at startup/setup
        	// so from then on these devices will be with lables.
		console.log (dev)
        	for (var i = 0; i<dev.length; i++) 
		{
			console.log ("[DEVICE] Type: "+dev[i].kind+" "+JSON.stringify (dev[i]))
        	}
    	}).catch(function (e)
    	{
        	console.error("Error enumerating devices", e);
    	});
}

var CALLS = {};

var CALL_COUNT = 0;

var WSHOST = "wss://"+VA_SIP_HOST+":8089/ws";


var VOICEAPPS_CHANSTATE = [
[],
["","Outgoing Call","Dialing","Connected","Call Ended","Call Ended",""],
["","Incoming Call","Ringing","Connected","Call Ended","Call Ended",""]
];

function VOICEAPPS_SESSION (_leg)
{
	this.session = null;
	this.leg = _leg;
	this.remoteStream = null;
	this.mediaElement = null;
	this.el = null;
	this.ssid = null;
	this.ishold = false;
	this.ishold_ts = 0;
	this.hangup_ts = 0;

	const options = {
            requestDelegate: {
                onAccept: () => {
			console.log ("Hold accepted");
                   // this.held = hold;
                   // this.enableReceiverTracks(!this.held);
                   // this.enableSenderTracks(!this.held && !this.muted);
                   // if (this.delegate && this.delegate.onCallHold) {
                   //     this.delegate.onCallHold(this.held);
                   // }
                },
                onReject: () => {
			console.log ("Hold rejected");
                   // this.logger.warn(`[${this.id}] re-invite request was rejected`);
                   // this.enableReceiverTracks(!this.held);
                   // this.enableSenderTracks(!this.held && !this.muted);
                   // if (this.delegate && this.delegate.onCallHold) {
                   //     this.delegate.onCallHold(this.held);
                   // }
                }
            }
        };

	this.handleSessionState = function () 
	{
		console.log ("VOICEAPPS_SESSION handleSessionState: "+this.session.id+" leg:"+this.leg);
		// console.log ("displayName: "+this.session.remoteIdentity.displayName);
		// console.log (this.session);

		this.session.delegate = { onCallHold: function (h) { console.log ("[OnCallHold] "); } };

		var k = re["activities_k"]
		var r = re["r_"][0].slice(0);
		this.ssid = this.session.id;
		r[0] = this.ssid;
		r[k["src_address"][0]] = this.session.remoteIdentity.uri.user;
		r[k["src_usr"][0]] = VOICEAPPS_UA.uao.cid_num;
		r[k["src_vector"][0]] = this.leg;
		r[k["src_ts"][0]] = ""+((Date.now ()/1000)-ra_ts);
		r[k["src_callid"][0]] = this.ssid.substr (0,20);
		if (this.session.remoteIdentity.displayName) r[1]=this.session.remoteIdentity.displayName;
		var p = document.getElementById ("call_sessions");
		var el_ = document.createElement ("P"); 
		el_.id = this.ssid.substr (0,20);
		p.insertBefore (el_, null); //p.firstChild);
		var el = nd (el_, te["call_session"], [(this.leg==1?"/helpline/images/dialtone.wav":"/helpline/images/earlymedia.mp3"),"noop"], r, [2]);
		el = el.parentNode.parentNode;
		this.el = el;
		var coll = el.childNodes[1].childNodes[1].childNodes;
		var cur_state = 0;

		CALL_COUNT++;
		notifs ();

		this.mediaElement = coll[5].firstChild; // _(el, "au").firstChild;
		this.mediaElement.volume = 0.3; // this.leg==1?0.3:0.9;
		this.mediaElement.play ();
		this.mediaElement.loop = true;

		var me = this;

		this.session.stateChange.addListener (function (new_state)
		{

			console.log ("VOICEAPPS_SESSION stateChange: "+new_state);
			// console.log (me.session)

			var state = cur_state;

			switch (new_state) 
			{
			case SIP.SessionState.Initial:
				state = 1;
				break;
	
			case SIP.SessionState.Establishing:
				state = 2;
				console.log ("VOICEAPPS_SESSION: establishing..."+me.session.id); // Session is establishing
				break;
	
			case SIP.SessionState.Established:
				state = 3;
				console.log ("VOICEAPPS_SESSION: established");
				me.mediaElement.volume = 1; // this.leg==1?0.3:0.9;
				VOICEAPPS_UA.connect_media (me.session, me.mediaElement);
				break;
	
			case SIP.SessionState.Terminating:
				state = 4;
				console.log ("VOICEAPPS_SESSION: Terminating");
	
			case SIP.SessionState.Terminated:
				state = 5;
				console.log ("VOICEAPPS_SESSION: Terminated "+me.session.id);
			        VOICEAPPS_UA.cleanup_media (me.mediaElement);
				if (el) 
				{ 
					var toolbar = document.getElementById ("vv").childNodes[1].firstChild;
					var a = {}
					argv (el, a); 
					me.hangup_ts = (Math.ceil ((Date.now()/1000)));
					a.src_ts_end = ""+me.hangup_ts; // duration in seconds
					a.src_status = a.src_state+"-"+a.src_vector+"-"+a.src_orig;
					a.src_status_duration = a.src_ts_end-a.src_state_ts;
					a.src_duration = me.hangup_ts-a.src_ts;	
					if (toolbar && toolbar.id==a.src_uid) call_popup_end (a.src_ts_end);
					p.removeChild (el); 
					el=null;
					CALL_COUNT--;
					notifs ();
					// var p_ = document.getElementById ("vt_activity");
					// url (p_, "activity_call", "activities", "", null, 2, a, "POST"); //depricated
				}
				// NB CALLS cleanup happens VOICEAPP_UA.callended
				break;
	
			default:
				console.error ("VOICEAPPS_SESSION: Unknown state");
				break;
			}

			if (cur_state != state) // update ts
			{
				coll[0].childNodes[1].innerHTML = "0:00";
				coll[0].childNodes[2].value = ""+(Date.now ()/1000)-ra_ts;
			}

			// coll[1].childNodes[1].innerHTML = VOICEAPPS_CHANSTATE[me.leg][state]; // update status

			if (state<3) // update ring tone
			{
				me.mediaElement.src = "/helpline/images/earlymedia.mp3";
				me.mediaElement.play ();
				me.mediaElement.loop = true;
			}

			if (state==3) // change buttons
			{
				coll[2].innerHTML = "";
				// nd (coll[2], te["call_session_btns_connected"], [], [], [0]);	
				//coll[3].innerHTML = "";
				//nd (coll[3], te["call_session_actions"], [], [], [0]);	
			}

			cur_state = state;
		});
	}
}

var VOICEAPPS_UA =
{
	UA : null,
	REG : null,
	attemptingReconnection : false,
	uao : 
	{
		userAgentString: "VoiceApps UA (SIP.js)",
		displayName: null,
		uri: null,
		authorizationUsername: null, 
		authorizationPassword: '23kdefrtgos09812100',
		delegate: { onInvite: null },
	    	transportOptions: 
		{
			server : WSHOST,
			//traceSip: true,
			log: { level:"log" },
		},
		log: { level:"log" },
	}
}

VOICEAPPS_UA.connect = function (exten)
{
	VOICEAPPS_UA.uao.cid_num = exten; 
	VOICEAPPS_UA.uao.cid_name = exten; 
	VOICEAPPS_UA.uao.displayName = exten; 
	VOICEAPPS_UA.uao.uri =  SIP.UserAgent.makeURI ("sip:"+VA_SIP_USER_PREFIX+exten+"@"+VA_SIP_HOST);
	VOICEAPPS_UA.uao.authorizationUsername = VA_SIP_USER_PREFIX+exten;
	VOICEAPPS_UA.uao.authorizationPassword = VA_SIP_PASS_PREFIX+exten;
	if (VA_SIP_PASS_PREFIX=="23kdefrtgos09812100") VOICEAPPS_UA.uao.authorizationPassword = "23kdefrtgos09812100";
	VOICEAPPS_UA.uao.delegate.onConnect = VOICEAPPS_UA.on_connect;
	VOICEAPPS_UA.uao.delegate.onDisconnect = VOICEAPPS_UA.on_disconnect;
	VOICEAPPS_UA.uao.delegate.onInvite = VOICEAPPS_UA.on_invite;
	VOICEAPPS_UA.uao.delegate.onMessage = VOICEAPPS_UA.on_msg;
	VOICEAPPS_UA.uao.delegate.onNotify = VOICEAPPS_UA.on_notify;
	VOICEAPPS_UA.UA = new SIP.UserAgent (VOICEAPPS_UA.uao);  // UserAgent
	VOICEAPPS_UA.REG = new SIP.Registerer (VOICEAPPS_UA.UA, {});
	VOICEAPPS_UA.UA.start()
	.catch((error) =>
	{
		console.log ("[UA start failed] "+error);
	 	VOICEAPPS_UA.re_connect (["xx y gp cr","Cannot connect to server. Check if server is online."])
        });
}

VOICEAPPS_UA.disconnect = function ()
{
	if (VOICEAPPS_UA.REG) VOICEAPPS_UA.REG.unregister();
}

VOICEAPPS_UA.re_connect = function (nbr, t=1)
{
	var p = document.getElementById ("phone_status"); // show error
	p.innerHTML = "";
	nd (p, te["nb"], [], nbr, [0])

	if (t!=1) return;

	// Reconnection attempt already in progress
	if (VOICEAPPS_UA.attemptingReconnection) { return; }
    
	// We're attempting a reconnection
	VOICEAPPS_UA.attemptingReconnection = true;
	setTimeout(() => 
	{  
		VOICEAPPS_UA.re_connect (["xx y gp cr","Retrying ..."])
      
		VOICEAPPS_UA.UA.reconnect().then(() => 
		{
			console.log ("[UA.reconnect successful] "+VOICEAPPS_UA.uao.displayName);
			// Reconnect attempt succeeded
			VOICEAPPS_UA.attemptingReconnection = false;
			VOICEAPPS_UA.re_connect (["xx y",("Extension "+VOICEAPPS_UA.uao.displayName)], 0)
           	})
           	.catch ((error) => 
		{
			console.log ("[UA.reconnect failed] "+error);
			// Reconnect attempt failed
			VOICEAPPS_UA.attemptingReconnection = false;
			VOICEAPPS_UA.re_connect (["xx y gp cr","Reconnect Failed. Retrying in 3sec"])
           	});
	}, 3000);

}

VOICEAPPS_UA.on_connect = function ()
{
	console.log ("[send registeration] "+ JSON.stringify (VOICEAPPS_UA.uao));
	VOICEAPPS_UA.REG.register()
	.then (() =>
	{
		VOICEAPPS_UA.re_connect (["xx y cd",("Extension "+VOICEAPPS_UA.uao.displayName)], 0);
	})
	.catch ((error) => 
	{
		console.log ("[Registration Failed] "+error)
	 	VOICEAPPS_UA.re_connect (["xx y gp cr",e], 0)
		return;
	})
}

VOICEAPPS_UA.on_disconnect = function (e)
{
	console.log ("[disconnected] "+JSON.stringify (e))
	VOICEAPPS_UA.REG.unregister()
	.catch((error) =>
	{
              console.log ("[Unregister Error] "+error);
        });

	// Only attempt to reconnect if network/server dropped the connection (if there is an error)
	//if (e) 
	{
	    	 VOICEAPPS_UA.re_connect (["xx y gp cr","Disconnected"])
  	}
}

VOICEAPPS_UA.on_msg = function (e)
{
	console.log ("ON__MSG: "+JSON.stringify (e))
}

VOICEAPPS_UA.on_notify = function (e)
{
	console.log ("ON__NOTIFY: "+JSON.stringify (e))
}

VOICEAPPS_UA.sethold = function (va, hold) 
{
 
     	const sessionDescriptionHandlerOptions = va.session.sessionDescriptionHandlerOptionsReInvite;
        sessionDescriptionHandlerOptions.hold = hold;
        va.session.sessionDescriptionHandlerOptionsReInvite = sessionDescriptionHandlerOptions;
        // Send re-INVITE
        return va.session.invite (va.options).then (() => 
        {
        	var pc = va.session.sessionDescriptionHandler.peerConnection;
		pc.getSenders().forEach ((stream) => 
		{
			//console.log (stream)
			stream.track.enabled = !hold;
			console.log ("Sender TRack Status ("+hold+") "+stream.track.enabled)
    		});
    		
		va.ishold = hold;
		va.ishold_ts = Date.now ()/1000;
		console.log ("hold is: "+hold);
		call_popup_hold_state (va.el, hold); // update hold state in toolbar
		call_popup_upd (va.el.childNodes[1].childNodes[1].lastChild.firstChild); 
		
        })
	.catch((error) => 
	{
		console.log ("hold errror: "+error);
	});
}

VOICEAPPS_UA.endcall = function (session, leg) 
{
	switch (session.state) 
	{
	case SIP.SessionState.Initial:
	case SIP.SessionState.Establishing:

	     	 if (leg==1) //session instanceOf SIP.Inviter) 
		 {
     		   session.cancel(); // outgoing session
     		 } else {
     		    session.reject();  // incoming session
     		}
     		break;

    	case SIP.SessionState.Established:
    		 session.bye();
		break;

	case SIP.SessionState.Terminating:
	case SIP.SessionState.Terminated:
      		break;
   	} 
}

VOICEAPPS_UA.cleanup_media = function (mediaElement)
{
	mediaElement.srcObject = null;
	mediaElement.pause();
}

VOICEAPPS_UA.connect_media = function (session, mediaElement) 
{
	var remoteStream = new MediaStream ();
	session.sessionDescriptionHandler.peerConnection.getReceivers().forEach (function (receiver) 
	{
	        if (receiver.track) 
		{
			// console.log (" + add track "+remoteStream + " " + mediaElement)
	            remoteStream.addTrack (receiver.track);
	        }
	});
	mediaElement.loop = false;
	mediaElement.srcObject = remoteStream;
	mediaElement.play ();
}

VOICEAPPS_UA.vs_cleanup = function () 
{
	var k = Object.keys (CALLS);
	for (var i=0; i<k.length; i++)
	{
		if (CALLS[k[i]].hangup_ts>0) delete CALLS[k[i]];
	}
	CALL_COUNT = Object.keys (CALLS).length;
}

VOICEAPPS_UA.on_invite = function (session) 
{
	VOICEAPPS_UA.vs_cleanup ();
	var dn = session.remoteIdentity.displayName;	
	var vs = new VOICEAPPS_SESSION (dn=="Autodial"?1:2);
	vs.session = session;
	vs.handleSessionState ();
	CALLS[vs.ssid] = vs ;
	
	console.log ("[on_invite] "+ dn+" | "+JSON.stringify (session.remoteIdentity))
		
	if (dn=="Autodial" || dn=="AgentLogin" || dn=="Supervisor")
	{
		session.accept ();
	}
}

VOICEAPPS_UA.dial = function (dial_str)
{
    	VOICEAPPS_UA.vs_cleanup ();
	// TODO: check state of UA

	var target = SIP.UserAgent.makeURI (("sip:"+dial_str+"@"+VA_SIP_HOST));   
	if (!target) 
	{
		console.error ("VOICEAPPS:  dial failed: makeURI failed.");
		return;
    	}
	
	console.log ("VOICEAPPS:   dial start"); // INVITE sent
			
	var vs = new VOICEAPPS_SESSION (1);
	vs.session = new SIP.Inviter (this.UA, target, { sessionDescriptionHandlerOptions: { constraints: { audio: true, video: false } } } );
	console.log ("VOICEAPPS:   dial new session created"); // INVITE sent
    	vs.handleSessionState ();
    	
    	console.log ("VOICEAPPS:   dial: state handled"); // INVITE sent
    	
	CALLS[vs.ssid] = vs;
	vs.session.invite().then (function () 
	{
		console.log ("VOICEAPPS:   Invite sent"); // INVITE sent
	})["catch"](function (error) 
	{
		console.error ("VOICEAPPS:  Invite failed "+error);
		// INVITE did not send
	});
}

// ----------------------------

function _ami_action (el, o, action)
{
	var u = el.id.split ("-")
	o.action = action;
	console.log ("[ami_action] "+JSON.stringify (o)+" | "+el);
	url (__(el), u[0], u[1], "", null, 2, o, "POST");
}

function _kickout (ev)
{
	var o = {};
	_ami_action (this, o, "6");	
	// boo (ev)
}

function _add_action (ev)
{
	var u = this.id.split ("-");
	var p = __(this,"ve")
	var el = _(document.getElementById ("call_sessions"), __(p,"vddvw").childNodes[1].id);
	var o = {}
	argv (p, o); console.log ("add_action|"+el.id+"|"+JSON.stringify (o))
	argv (__(el,"va"), o);	
	_ami_action (this, o, u[2]);	
	boo (ev);
}

function _add_dial (ev) 
{
	var u = this.id.split ("-"); // todo: inv
	var p = __(this,"ve")
	var el = _(document.getElementById ("call_sessions"), p.parentNode.id);
	var o = {}
	argv (p, o);
	if (el==null) 
	{
		this.parentNode.nextSibling.innerHTML = "<div class='x y'><div class='x08 y gp cr'>Call has already ended</div></div>";
		return;
	}
	argv (__(el,"va"), o);	
	// if (o.cbid.length>0) o.chan2=""; // unset chan2 to remove it from unnecesary redirect
	_ami_action (this, o, "2");	
}

function _add_dial_form ()
{
	var p = document.getElementById ("vp");
	var u = this.id.split ("-");
	var o = {};
	var r_ = ra[u[1]][0].slice (0)
	var el = null;
	argv (this, o, "id");	
	el = _(document.getElementById ("call_sessions"), o._uid);
	argv (__(el,"va"), o);	
	console.log ("[_add_dial_form] "+JSON.stringify (o))
	r_[AMI.CHAN_UNIQUEID] = o._uid;
	vp (p);
	nd (p, te[u[0]], [], r_, [0]);
	ldami (re["channels"]);
}

// ------------------------------------

function phone_hangup (id)
{
	var vs = CALLS[id]
	console.log ("hangup---------------------"+id)
	VOICEAPPS_UA.endcall (vs.session, vs.leg);
}

function _hangup (ev)
{
	var id = __(this,"va").previousSibling.value;
	phone_hangup (id)
	boo (ev);
}

function _hold (ev)
{
	var id = __(this,"va").previousSibling.value;
	var vs= CALLS[id]
	console.log ("hold("+vs.ishold+")---------------------"+id)
	VOICEAPPS_UA.sethold (vs, !vs.ishold);
	boo (ev);
}

function _answer (ev)
{
	var id = __(this,"va").previousSibling.value;
	CALLS[id].session.accept ({ sessionDescriptionHandlerOptions: { constraints: { audio: true, video: false } } });
	console.log ("answer---------------------"+id)
	boo (ev);
}

function _dial (ev)
{
	VOICEAPPS_UA.dial (this.previousSibling.firstChild.value);
	boo (ev);
}

