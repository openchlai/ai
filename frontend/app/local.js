

rk["local_metrics"] = ["count","percent","waittime","talktime","holdtime"];
re["local_metrics"] = 
{
"count":	["count",	"branch,vector,hangup_status","","count",	"Count","0","local_rpt_count","local_rpt-locals-@:1:@"],
"percent":	["percent",	"branch,vector,hangup_status","","percent",	"Percent","1","local_rpt_percent","local_rpt-locals-@:1:@"],
"waittime":	["waittime", 	"branch,vector,hangup_status","","waittime",	"Wait-Time","4","local_rpt_waittime","local_rpt-locals-@:1:@"],
"talktime":	["talktime", 	"branch,vector,hangup_status","","talktime",	"Talk-Time","5","local_rpt_talktime","local_rpt-locals-@:1:@"],
"holdtime":	["holdtime",	"branch,vector,hangup_status","","holdtime",	"Hold-Time","6","local_rpt_holdtime","local_rpt-locals-@:1:@"],
};

re["local_k"] = 
{
	"trunk":["trunk","DID"],
	"branch":["branch","Branch"],
	"vector":["vector","Direction"],
	"usr":["usr","Extension"],
	"hangup_status":["hangup_status","Hangup Status"],
	"sla_wait_band":["sla_wait_band","SLA Band"],
	// category
};

te["local_k_tag"] = { "rpt_axis_tag":["::local_k:0:1","xaxis"] };

te["local_k_r"] = { "rpt_axis_r":["xaxis","local_k_tag","::local_k:0:1"] };

te["local_rpt_h"] = { rpt:["%3","::local_metrics:3:4","local_k_r","%1","local_k","local_k_tag","%1", "%2", "local_rpt"] };

te["local_rpt"] = { c:[ { local_rpt_h:[] }, { div:["","rpt_vw_bar_stacked-locals"], rpt_vw_bar_stacked:[] } ] };

te["local_rpt_holdtime"] = { c:[ { u:["local_rpt_h","local_metrics","holdtime"] }, { div:["","rpt_vw_bar_stacked-locals"], urpt:[] } ] };
te["local_rpt_talktime"] = { c:[ { u:["local_rpt_h","local_metrics","talktime"] }, { div:["","rpt_vw_bar_stacked-locals"], urpt:[] } ] };
te["local_rpt_waittime"] = { c:[ { u:["local_rpt_h","local_metrics","waittime"] }, { div:["","rpt_vw_bar_stacked-locals"], urpt:[] } ] };
te["local_rpt_percent"] = { c:[ { u:["local_rpt_h","local_metrics","percent"] }, { div:["","rpt_vw_bar_stacked-locals"], urpt:[] } ] };
te["local_rpt_count"] = { c:[ { u:["local_rpt_h","local_metrics","count"] }, { div:["","rpt_vw_bar_stacked-locals"], urpt:[] } ] };

te["local_rpt_metric_tab"] = { div:["c x","%7"], c:
[
	{ arg:["","","0"] },
	{ input:["g","","local_metric","%5","radio","%9"] },
	{ li:["opth x y tc cb","%6","%4"], ev:["_tab"] } // _rpt_chk
]};

te["local_rpt_main"] = { c:
[
	{ div:["tt s bb","vb"], c:
	[
		{ s:["c x y cd","Metric:"] },
		{ uchk:["local_rpt_metric_tab","count","local_metrics"] },
		// { ac:["d","","","x y","Save"] },
		{ div:["e"] }
	]},
	{ div:["","vrpt"], c:
	[
		{ div:[], c:[ { input:["g","","local_rptv","0","radio","1"] }, { p:["tabv ","vt"], local_rpt_count:[] } ]},
		{ div:[], c:[ { input:["g","","local_rptv","1","radio"] }, { p:["tabv","vt"] } ] },
		{ div:[], c:[ { input:["g","","local_rptv","2","radio"] }, { p:["tabv","vt"] } ] },
		{ div:[], c:[ { input:["g","","local_rptv","3","radio"] }, { p:["tabv","vt"] } ] },
		{ div:[], c:[ { input:["g","","local_rptv","4","radio"] }, { p:["tabv","vt"] } ] },
		{ div:[], c:[ { input:["g","","local_rptv","5","radio"] }, { p:["tabv","vt"] } ] },
		{ div:[], c:[ { input:["g","","local_rptv","6","radio"] }, { p:["tabv","vt"] } ] },
		{ div:[], c:[ { input:["g","","local_rptv","7","radio"] }, { p:["tabv","vt"] } ] },
	]}
]};

// ----------------------------------------------

te["local_f_tags"] = { c: 
[
	{ f:["Date",":k:locals_f:chan_ts",			" :d:dmy:0: "," chan_ts"] },
	{ f:["Branch",":k:locals_f:branch",			" ::branch:0:1"," branch"] },
	{ f:["Direction",":k:locals_f:vector",			" ::vector:0:1"," vector"] },
	{ f:["Trunk",":k:locals_f:trunk",			" %0"," trunk"] },
	{ f:["Phone",":k:locals_f:phone",			" %0"," phone"] },
	{ f:["Extension",":k:locals_f:usr",			" %0"," usr"] },
	{ f:["Wait Time",":k:locals_f:wait_time_tot",		" %0"," wait_time_tot"] },
	{ f:["Talk Time",":k:locals_f:talk_time",		" %0"," talk_time"] },
	{ f:["Hangup Reason",":k:locals_f:hangup_reason",	" ::hangup_reason:0:1"," hangup_reason"] },
	{ f:["Hangup Status",":k:locals_f:hangup_status",	" ::hangup_status:0:1"," hangup_status"] },
	{ div:["e"] }
]};

te["local_f"] = { div:["w70 ma bd sh__ y gw"], c: // "vddvw"], ev:["_undd"
[
	{ s:["x20 yy b bb_","Filters"] },
	{ div:["x15 tt b20"], c:
	[
		{ div:["xx yy"], kf_d:["Date"," :d:dmy:0: ","chan_ts",":k:locals_f:chan_ts","chan_ts",":k:locals_f:chan_ts"] },
		// { div:["xx yy"], kf_c:["Branch","tag-o-branch-::branch:0:1", 	":k:locals_f:branch"," ::branch:0:1"," branch",		":k:locals_f:branch","branch", " branch"," ::branch:0:1"," "] },
		{ div:["xx yy"], kf_c:["Direction","tag-o-vector-::vector:0:1",  	":k:locals_f:vector"," ::vector:0:1"," vector", 		":k:locals_f:vector","vector", " vector"," ::vector:0:1"," "] },		
		{ div:["xx yy"], kf_s:["Trunk DID","trunk",":k:locals_f:trunk"] },
		{ div:["xx yy"], kf_s:["Phone","phone",":k:locals_f:phone"] },
		{ div:["xx yy"], kf_s:["Extension","usr",":k:locals_f:usr"] },
		{ div:["xx yy"], kf_s:["Wait Time","wait_time_tot",":k:locals_f:wait_time_tot"] },
		{ div:["xx yy"], kf_s:["Talk Time","talk_time",":k:locals_f:talk_time"] },
		{ div:["xx yy"], kf_c:["Hangup Reason","tag-o-hangup_reason-::hangup_reason:0:1", 	":k:locals_f:hangup_reason"," ::hangup_reason:0:1"," hangup_reason", 	":k:locals_f:hangup_reason", "hangup_reason", " hangup_reason"," ::hangup_reason:0:1"," "] },
		{ div:["xx yy"], kf_c:["Hangup Status","tag-o-hangup_status-::hangup_status:0:1", 	":k:locals_f:hangup_status"," ::hangup_status:0:1"," hangup_status",	":k:locals_f:hangup_status", "hangup_status", " hangup_status"," ::hangup_status:0:1"," "] },
	]},
	{ div:["x20 yy"], c:
	[
		{ div:["c w06 r02"], c:[ { ac:["ad btn","local_f_tags-locals_f","_applyf","x y w05 gbl bd ba_br cw tc","Apply"] }, { s:["y07 bd b savl","..."] } ] },
		{ div:["c l20","va"], ac:["ay","","_vpclose","x y w05 ba_bl bd tc cbr","Cancel"], c:[ { p:["g","o"], arg:["",".id",""] } ] },
		{ div:["e"] }
	]}
]};

// ----------------------------------------------


te["local_footer"] = { div:["gw x mtn08 bt"], c:
[
	{ div:["d y07"], pg:["pgto","local_list-locals"," dh","da dl","local_list-locals"," dh","da dr"] },
	{ div:["e"] }
]};

te["local_r"] = { div:[], c:
[
	{ li:["w160 gw","vg"], s:["content-hidden",""], c:
	[
		{ ac:["c w14","local_vw_id-locals","","cb",""], c:
		[
			{ s:["tt b03 bb2_bl h01_ xx b cb content-shown_",":d:dmyhn:1: "] },  
			{ s:["tt b05 h01_ xx  content-hidden_",":d:dmyhn:1: "] }, 
			{ arg:[".id","","%0"] } 
		] },
		{ div:["c w10"], s:["tt b05 h01_  xx","::vector:22:11"] },
		{ div:["c w08"], s:["tt b05 h01_  xx","%6"] },
		{ div:["c w02"], s:["tt b05 h01_ xx","::vector:22:2"] },
		{ div:["c w14"], s:["tt b05 h01_  xx","%5"] },
	//	{ div:["c w10"], s:["tt b05 h01_  xx","::branch:25:1"] }, 
		{ div:["c w10"], s:["tt b05 h01_  xx tr",":h:ms:10:"] },
		{ div:["c w10"], s:["tt b05 h01_  xx tr",":h:ms:11:"] },
		{ div:["c w12"], s:["tt b05 h01_  xx tr","%12"] },
		{ div:["c w12"], s:["tt b05 h01_  xx tr","%13"] },
		{ div:["c"], s:["tt b05 h01_ xx tr","%26"] },
		{ div:["e"] }
	]},
	{ div:["g x15 y15 gwd bb_","vdd"], c:
	[

	]}
]};

te["local_k"] = { div:["w160 bt bb"], s:["",""], c: // activate filter ctx
[
	{ k_a:["c w14","local_rr-locals","cd st","Date","da db","chan_ts",":k:locals_k:chan_ts:2"] },
	{ k_a:["c w10","local_rr-locals","cd st","Direction","da db","vector",":k:locals_k:vector:2"] },
	{ k_a:["c w10","local_rr-locals","cd","Extension","da db","usr",":k:locals_k:usr:2"] },
	{ k_a:["c w14","local_rr-locals","cd","Phone","da db","phone",":k:locals_k:phone:2"] },
	// { k_a:["c w10","local_rr-locals","cd","Branch","da db","branch",":k:locals_k:branch:2"] },
	{ k_a:["c w10","local_rr-locals","w08 cd tr","Wait Time","da db","wait_time_tot",":k:locals_k:wait_time_tot:2"] },
	{ k_a:["c w10","local_rr-locals","w08 cd tr","Talk Time","da db","talk_time",":k:locals_k:talk_time:2"] },
	{ k_a:["c w12","local_rr-locals","w10 cd tr","Hangup By","da db","hangup_reason",":k:locals_k:hangup_reason:2"] },
	{ k_a:["c w12","local_rr-locals","w10 cd tr","Hangup Status","da db","hangup_status",":k:locals_k:hangup_status:2"] },
	//{ k_a:["c w14","local_rr-locals","w12 cd tr","Disposition","da db","category",":k:locals_k:category:2"] },
	//{ k_a:["c w14","local_rr-locals","w12 cd tr","QA Done","da db","qa_score",":k:locals_k:qa_score:2"] },
	{ div:["e"] }
]};

te["local_nb"] = { div:[], c:[ { u:["nb","locals_nb"] }, { div:["e"] } ] };

te["local_title"] = { div:[] }; 

te["local_list"] = { list:["local_title","local_nb","bl br oh","local_k","local_r","locals","local_footer"] };

te["local_main"] = { c:
[
	{ div:["t15","vb"], c:
	[
		{ div:["c"], c:
		[
			{ arg:["","","0"] },
			{ input:["g","","locals_t","0","radio","1"] },
			{ ac:["","local_list-locals","_tab","x y cb b n","Call History &gt; Internal Calls"] }, 
		]},
		{ div:["d l15 aa"], ac:["","locals","_csv","x cd s",""], c:
		[ 
			{ div:["c t04"], c:[ { img:["","","/voiceapps/images/download.png", "16"] } ] },
			{ div:["c x y","","CSV"] }, 
			{ div:["e"] }
		]},
		{ div:["d l15","local_rpt-locals-@:1:"], c: // loaded only when tab contents are blank
		[
			{ arg:["","","0"] },
			{ input:["g","","locals_t","1","radio"] },
			{ ac:["c aa","local_rpt_main","_tab","x cd s",""], c:
			[
				{ div:["c t04"], c:[ { img:["","","/voiceapps/images/chart.png", "16"] } ] },
				{ div:["c x y","","Reports"] }, 
				{ div:["e"] }
			]},
			// { div:["d"], ac:["aa","","_dsdd","x02 t04 b02",""],  c:[ { div:["h02 w02 awb"] } ] },
			{ div:["e"] }
		]},
		{ div:["d l15","local_rpt-locals-@:1:"], c: // loaded only when tab contents are blank
		[
			{ arg:["","","0"] },
			{ input:["g","","locals_t","0","radio"] },
			{ ac:["c aa","local_list-locals","_tab","x cd s",""], c:
			[
				{ div:["c t04"], c:[ { img:["","","/voiceapps/images/list.png", "16"] } ] },
				{ div:["c x y","","List"] }, 
				{ div:["e"] }
			]},
			// { div:["d"], ac:["aa","","_dsdd","x02 t04 b02",""],  c:[ { div:["h02 w02 awb"] } ] },
			{ div:["e"] }
		]},
		{ div:["d"], ac:["aa","local_f-locals_f","_vpf","x cd s",""], c:
		[ 
			{ div:["c t04"], c:[ { img:["","","/voiceapps/images/filter.png", "16"] } ] },
			{ div:["c x y","","Filter"] }, 
			{ div:["e"] }
		]},
		{ div:["e"], c:[ { arg:["","","local_list-locals"] }, { arg:["","","0"] }, { arg:["","","0"] } ] }
	]},
	{ div:["ga x","vf"] },
	{ div:["t"], c:
	[
		{ div:[], c:[ { input:["g","","locals_v","0","radio","1"] }, { p:["tabv","vt"], local_list:[] } ] },
		{ div:[], c:[ { input:["g","","locals_v","1","radio"] }, { p:["tabv","vt"] } ] },				
	]}
]};
