
rk["ext_metric_tab"] = ["count","percent","uniquecallers","repeatcallers","waittime","talktime","holdtime"];
re["ext_metric_tab"] = 
{
"count":	["count",	"Count","0","call_rpt_count","call_rpt-calls-@:1:0:0"],
"percent":	["percent",	"Percent","1","call_rpt_percent","call_rpt-calls-@:1:1:1"],
"uniquecallers":["uniquecallers", "Unique Callers","2","call_rpt_uniquecallers","call_rpt-calls-@:1:2:2"],
"repeatcallers":["repeatcallers", "Repeat Callers","3","call_rpt_repeatcallers","call_rpt-calls-@:1:3:3"],
"waittime":	["waittime", 	"Avg Wait Time (in seconds)","4","call_rpt_waittime","call_rpt-calls-@:1:4:4"],
"talktime":	["talktime", 	"Avg Talk Time (in seconds)","5","call_rpt_talktime","call_rpt-calls-@:1:5:5"],
"holdtime":	["holdtime",	"Avg Hold Time (in seconds)","6","call_rpt_holdtime","call_rpt-calls-@:1:6:6"],
"billing":	["billing",	"Billing (in Kshs)","7","call_rpt_billing","call_rpt-calls-@:1:7:7"],
}; 

te["ext_rpt_metric_tab"] = { div:["c x","%4"], c:
[
	{ arg:["","","0"] },
	{ input:["g","","call_metric","%2","radio","%9"] },
	{ li:["opth x y tc cb","%3","%1"], ev:["_tab"] }
]};

re["ext_k"] = 
{
	// "trunk":["trunk","DID"],
	"vector":["vector","Direction"],
	"usr":["usr","Extension"],
	"hangup_status":["hangup_status","Hangup Status"],
	"sla_wait_band":["sla_wait_band","SLA Band"],
	// category
};

te["ext_k_tag"] = { "rpt_axis_tag":["::call_k:0:1","xaxis"] };

te["ext_k_r"] = { "rpt_axis_r":["xaxis","call_k_tag","::call_k:0:1"] };

te["ext_rpt_"] = { c: // todo: load rpt_hdr params from db
[ 
	{ form:["tt","vrpt"], rpt_hdr:[null, "call_k_r",null,"call_k", "call_k_tag",null, null,"dist", null,null] }, 
	{ div:["","call_rpt_vw-calls"], urpt:[] } 
]};

te["ext_rpt"] = { ext_rpt_:["::call_metrics:4:1","%2","%2","%3","%4","%7"] };  // todo: load saved report

te["ext_rpt_count"] = { ext_rpt_:["Count","vector,hangup_status","vector,hangup_status","-","count","0"] };

te["ext_rpt_main"] = { c:
[
	{ div:["s bb_ tt","vb"], c:
	[
		{ s:["c x y cd","Metric:"] },
		{ uchk:["ext_rpt_metric_tab","count","ext_metric_tab"] },
		// + add // todo add mutiple metrics to same canvas // then multi-metric with from different resources
		{ div:["d"], c:
		[
			{ div:["w12 ay","va"], ac:["","","_dd","x cd",""], c:
			[
				{ div:["d w02 t04"], s:["h02 w02 awb",""] },
				{ s:["d x y","Saved Reports"] }, 
				{ div:["e"] }
			]},			
			{ div:["dd mln13 w25 ba sh gw cb","vdd"], ev:["_undd"], c:
			[
				{s:["xx y cd","- Saved Reports List -"] }
			]}
		]},
		{ div:["e"] }
	]},
	{ div:["","vrpt"], c:
	[
		{ div:[], c:[ { input:["g","","call_rptv","0","radio","1"] }, { p:["tabv ","vt"], call_rpt_count:[] } ]},
		{ div:[], c:[ { input:["g","","call_rptv","0","radio"] }, { p:["tabv","vt"] } ] },
		{ div:[], c:[ { input:["g","","call_rptv","0","radio"] }, { p:["tabv","vt"] } ] },
		{ div:[], c:[ { input:["g","","call_rptv","0","radio"] }, { p:["tabv","vt"] } ] },
		{ div:[], c:[ { input:["g","","call_rptv","0","radio"] }, { p:["tabv","vt"] } ] },
		{ div:[], c:[ { input:["g","","call_rptv","0","radio"] }, { p:["tabv","vt"] } ] },
		{ div:[], c:[ { input:["g","","call_rptv","0","radio"] }, { p:["tabv","vt"] } ] },
		{ div:[], c:[ { input:["g","","call_rptv","0","radio"] }, { p:["tabv","vt"] } ] },
	]}
]};

// ----------------------------------------------

te["ext_f_tags"] = { c: 
[
	{ f:["Date",":k:exts_f:chan_ts",			" :d:dmy:0: "," chan_ts"," "] },
	{ f:["Direction",":k:exts_f:vector",			" ::vector:0:1"," vector"," "] },
	{ f:["Phone",":k:exts_f:phone",			" %0"," phone"," "] },
	{ f:["Extension",":k:exts_f:usr",			" %0"," usr"," "] },
	{ f:["Wait Time",":k:exts_f:wait_time_tot",		" %0"," wait_time_tot"," "] },
	{ f:["Talk Time",":k:exts_f:talk_time",		" %0"," talk_time"," "] },
	{ f:["Hold Time",":k:exts_f:hold_time",		" %0"," hold_time"," "] },
	{ f:["Hangup By",":k:exts_f:hangup_reason",		" ::hangup_reason:0:1"," hangup_reason"," "] },
	{ f:["Hangup Status",":k:exts_f:hangup_status",	" ::hangup_status:0:1"," hangup_status"," "] },
	{ f:["QA Done",":k:exts_f:qa_done",			" ::qa_done:0:1"," qa_done"," "] },
	{ div:["e"] }
]};


te["ext_f"] = { div:["w55 ma bd sh__ y gw","vddvf"], ev:["_undd"], c: 
[
	{ s:["x20 yy b bb_","Filters"] },
	{ div:["x15 tt b20"], c:
	[
		{ div:["xx yy"], kf_d:["Date"," :d:dmy:0: ","chan_ts",":k:exts_f:chan_ts","chan_ts",":k:exts_f:chan_ts"] },
		{ div:["xx yy"], kf_c:["Direction","tag-r_--o--::vector:0:1-vector-%0",  ":k:exts_f:vector"," ::vector:0:1"," vector"," %0", 	":k:exts_f:vector","vector", " vector"," ::vector:0:1"," "] },	
		{ div:["xx yy"], kf_s:["Phone","phone",":k:exts_f:phone"] },
		{ div:["xx yy"], kf_s:["Extension","usr",":k:exts_f:usr"] },
		{ div:["xx yy"], kf_s:["Wait Time","wait_time_tot",":k:exts_f:wait_time_tot"] },
		{ div:["xx yy"], kf_s:["Talk Time","talk_time",":k:exts_f:talk_time"] },
		{ div:["xx yy"], kf_s:["Hold Time","hold_time",":k:exts_f:hold_time"] },
		{ div:["xx yy"], kf_c:["Hangup By","tag-r_--o--::hangup_reason:0:1-hangup_reason-%0",  ":k:exts_f:hangup_reason"," ::hangup_reason:0:1"," hangup_reason"," %0", 	":k:exts_f:hangup_reason","hangup_reason", " hangup_reason"," ::hangup_reason:0:1"," "] },	
		{ div:["xx yy"], kf_c:["Hangup Status","tag-r_--o--::hangup_status:0:1-hangup_status-%0",  ":k:exts_f:hangup_status"," ::hangup_status:0:1"," hangup_status"," %0", 	":k:exts_f:hangup_status","hangup_status", " hangup_status"," ::hangup_status:0:1"," "] },
		// todo: category
	]},
	{ vp_apply:["ext_f_tags-exts_f"] }
]};

// ----------------------------------------------

te["ext_footer"] = { div:["gw x mtn08 ba"], c:
[
	{ div:["d y07"], pg:["pgto","ext_list-exts"," dh","da dl","ext_list-exts"," dh","da dr"] },
	{ div:["e"] }
]};

te["ext_r"] = { div:[], c:
[
	{ ac:["c w15","call_vw_id-calls","___vwr","cb",""], c:
	[
		{ s:["xx tt b05 h01_",":d:dmyhnr:1: "] },  
		{ arg:[".id","","%0"] } 
	]},
	{ div:["c w10"], s:["tt b05 h01_  xx",":v:calls:vector:vector:1"] },
	{ div:["c w14"], s:["tt b05 h01_  xx",":v:calls:phone"] },
	{ div:["c w16"], s:["tt b05 h01_  xx",""], c:
	[
		{ s:["c",":v:calls:vector:vector:2"] },
		{ s:["c x",":v:calls:usr"] },
		{ s:["c x",":v:calls:user_name"] },
		{ div:["e"] } 
	]},
	
	{ div:["c w08"], s:["tt b05 h01_  xx tr",":h:ms:10:"] },
	{ div:["c w08"], s:["tt b05 h01_  xx tr",":h:ms:28:"] },
	{ div:["c w08"], s:["tt b05 h01_  xx tr",":h:ms:11:"] },
	
	{ div:["c w12"], s:["tt b05 h01_  xx tr","::hangup_reason:12:1"] },
	{ div:["c w12"], s:["tt b05 h01_  xx tr","::hangup_status:13:1"] },
	
	{ div:["c w12"], s:["tt b05 h01_ xx tr",""] },
	{ div:["c w12"], s:["tt b05 h01_ xx tr",""] },
	
	{ div:["e"] }
]};

te["ext_k"] = { div:["w160 bt bb"], s:["",""], c: // activate filter ctx
[
	{ k_a:["c w15","call_rr-calls","cd st","Date","da db","chan_ts",":k:calls_k:chan_ts:2"] },
	{ k_a:["c w10","call_rr-calls","cd st","Direction","da db","vector",":k:calls_k:vector:2"] },
	{ k_a:["c w14","call_rr-calls","cd","Phone","da db","phone",":k:calls_k:phone:2"] },
	{ k_a:["c w16","call_rr-calls","cd","Extension","da db","usr",":k:calls_k:usr:2"] },
	
	{ k_a:["c w08","call_rr-calls"," cd tr","Wait Time","da db","wait_time_tot",":k:calls_k:wait_time_tot:2"] },
	{ k_a:["c w08","call_rr-calls"," cd tr","Hold Time","da db","hold_time",":k:calls_k:hold_time:2"] },
	{ k_a:["c w08","call_rr-calls"," cd tr","Talk Time","da db","talk_time",":k:calls_k:talk_time:2"] },
		
	{ k_a:["c w12","call_rr-calls","w10 cd tr","Hangup By","da db","hangup_reason",":k:calls_k:hangup_reason:2"] },
	{ k_a:["c w12","call_rr-calls","w10 cd tr","Hangup Status","da db","hangup_status",":k:calls_k:hangup_status:2"] },

	{ k_a:["c w12","call_rr-calls","w10 cd tr","Case ID","da db","category",":k:calls_k:case_id:2"] },	
	{ k_a:["c w12","call_rr-calls","w10 cd tr","Disposition","da db","category",":k:calls_k:disposition:2"] },
	{ k_a:["c w12","call_rr-calls","w10 cd tr","QA Done","da db","qa_done",":k:calls_k:qa_done:2"] },
	{ div:["e"] }
]};

te["ext_nb"] = { div:[], c:[ { u:["nb","exts_nb"] }, { div:["e"] } ] };

te["ext_title"] = { div:[] }; 

te["ext_list"] = { list:["ext_title","ext_nb","bl br ox","ext_k","ext_r","exts","ext_footer"] };

te["ext_main"] = { c:
[
	{ div:["y","vb"], c:
	[
		{ div:["c"], c:
		[
			{ input:["g","","exts_t_","0","radio","1"] },
			{ ac:["","ext_list-exts","_tab","x y cb b h2","Other Channels"] }, 
		]},
		{ div:["d","ext_rpt-exts-@:1:0"], c: 
		[
			{ arg:["","","0"] },
			{ input:["g","","exts_t_","1","radio"] },
			{ li:["opto x ba gw bdr s cb","ext_rpt_main"], ev:["_tab"], c:
			[
				{ s:["c l t h3_ micon","bar_chart"] },
				{ s:["c xx y","Reports"] }, 
				{ div:["e"] }
			]}
		]},
		{ div:["d "], c: 
		[
			{ arg:["","","0"] },
			{ input:["g","","exts_t_","0","radio","1"] },
			{ li:["opto x bl bt bb gw bdl s cb","ext_list-exts"], ev:["_tab"], c:
			[
				{ s:["c l t h3_ micon","list"] },
				{ div:["c xx y","","List"] }, 
				{ div:["e"] }
			]}
		]},
		{ div:["d x15 ay"], ac:["","exts","_xlsx","x t01 bd_ cd s",""], c:
		[ 
			{ s:["c t04 h3_ micon","download"] },
			{ div:["c x y","","XLSX"] }, 
			{ div:["e"] }
		]},
		{ div:["d"], ac:["ay","ext_f-exts_f","_vpf","x t01 cd s bd_",""], c:
		[ 
			{ s:["c t04 h3_ micon","filter_alt"] },
			{ div:["c x y","","Filter"] }, 
			{ div:["e"] }
		]},
		{ div:["e"], c:[ { arg:["","","ext_list-exts"] }, { arg:["","","0"] }, { arg:["","","0"] }, { arg:["","",""] } ] }
	]},
	{ div:["x bd","vf"], c:[ { li:["","ext_f-exts_f"], ev:["__vpf"], c:
	[

	]} ]},
	{ div:[], c:
	[
		{ div:[], c:[ { input:["g","","exts_v","0","radio","1"] }, { p:["tabv yy","vt"], ext_list:[] } ] },
		{ div:[], c:[ { input:["g","","exts_v","1","radio"] }, { p:["tabv","vt"] } ] },				
	]}
]};
	
te["exts"] = { c:
[
	{ div:["x25 tt s g","vb"], c:
	[
		
	]},
	{ div:["x y mt ml mb mr gw"], c: // tabs
	[
		{ div:[], c:[ { input:["g","","exts_mv","0","radio","1"] }, { div:["tabv gw bd x15 yy","vftab"], ext_main:[] } ] },
		{ div:[], c:[ { input:["g","","exts_mv","1","radio"] }, { div:["tabv","vftab"] } ] },
		{ div:[], c:[ { input:["g","","exts_mv","2","radio"] }, { div:["tabv","vftab"] } ] },
		{ div:[], c:[ { input:["g","","exts_mv","3","radio"] }, { div:["tabv","vftab"] } ] },
		{ div:[], c:[ { input:["g","","exts_mv","4","radio"] }, { div:["tabv","vftab"] } ] },
	]}
]};


