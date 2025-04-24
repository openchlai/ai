
rk["chanss_metrics"] = ["available","occupied","occupancy","availability"];
re["chanss_metrics"] = 
{
// availability
"availability":	["availability","usr","","availability","Availability-Rate (%)","3","chanss_rpt_availability","chanss_rpt-chanss-@:1:@"],
"occupancy":	["occupancy", 	"usr","","occupancy",	"Occupancy-Rate (%)","2","chanss_rpt_occupancy","chanss_rpt-chanss-@:1:@"],
"occupied":	["occupied",	"usr","","occupied",	"Occupied-Duration (in Hours)","1","chanss_rpt_occupied","chanss_rpt-chanss-@:1:@"],
"available":	["available",	"usr","","available",	"Available-Duration (in Hours)","0","chanss_rpt_available","chanss_rpt-chanss-@:1:@"],

};

re["chanss__k"] = 
{
	"usr":["usr","Extension"],
};

te["chanss_k_tag"] = { "rpt_axis_tag":["::chanss__k:0:1","xaxis"] };

te["chanss_k_r"] = { "rpt_axis_r":["xaxis","chanss_k_tag","::chanss__k:0:1"] };

// te["call_rpt_h"  ] = { rpt:["%3","::call_metrics:3:4",    "call_k_r","%1","call_k","call_k_tag","%1", "%2", "call_rpt"] };
te["chanss_rpt_h"] = { rpt:["%3","::chanss_metrics:3:4",  "chanss_k_r","%1","chanss__k","chanss_k_tag","%1",  "%2", "chanss_rpt"] };

te["chanss_rpt"] = { c:[ { chanss_rpt_h:[] }, { div:["","rpt_vw_bar_stacked-chanss"], rpt_vw_bar_stacked:[] } ] };

te["chanss_rpt_availability_"] = { c:[ { u:["chanss_rpt_h","chanss_metrics","availability"] }, { div:["","rpt_vw_bar_stacked-chanss"], urpt:[] } ] };
te["chanss_rpt_occupancy"] = { c:[ { u:["chanss_rpt_h","chanss_metrics","occupancy"] }, { div:["","rpt_vw_bar_stacked-chanss"], urpt:[] } ] };
te["chanss_rpt_occupied"] = { c:[ { u:["chanss_rpt_h","chanss_metrics","occupied"] }, { div:["","rpt_vw_bar_stacked-chanss"], urpt:[] } ] };
te["chanss_rpt_available"] = { c:[ { u:["chanss_rpt_h","chanss_metrics","available"] }, { div:["","rpt_vw_bar_stacked-chanss"], urpt:[] } ] };

te["chanss_rpt_metric_tab"] = { div:["c x","%7"], c:
[
	{ arg:["","","0"] },
	{ input:["g","","chanss_metric","%5","radio","%9"] },
	{ li:["opth x y tc cb","%6","%4"], ev:["_tab"] } // _rpt_chk
]};

te["chanss_rpt_main"] = { c:
[
	{ div:["bb s","vb"], c:
	[
		{ s:["c x y cd","Metric:"] },
		{ uchk:["chanss_rpt_metric_tab","available","chanss_metrics"] },
		// { ac:["d","","","x y","Save"] },
		{ div:["e"] }
	]},
	{ div:["","vrpt"], c:
	[
		{ div:[], c:[ { input:["g","","chanss_rptv","0","radio","1"] }, { p:["tabv ","vt"], chanss_rpt_available:[] } ] },
		{ div:[], c:[ { input:["g","","chanss_rptv","1","radio"] }, { p:["tabv","vt"] } ] },
		{ div:[], c:[ { input:["g","","chanss_rptv","2","radio"] }, { p:["tabv","vt"] } ] },
		{ div:[], c:[ { input:["g","","chanss_rptv","3","radio"] }, { p:["tabv","vt"] } ] },
		{ div:[], c:[ { input:["g","","chanss_rptv","4","radio"] }, { p:["tabv","vt"] } ] },
		{ div:[], c:[ { input:["g","","chanss_rptv","5","radio"] }, { p:["tabv","vt"] } ] },
		{ div:[], c:[ { input:["g","","chanss_rptv","6","radio"] }, { p:["tabv","vt"] } ] },
		{ div:[], c:[ { input:["g","","chanss_rptv","7","radio"] }, { p:["tabv","vt"] } ] },
	]}
]};

// --------------------------------------------------------------------------------

te["chanss_f_tags"] = { c: 
[
	{ f:["Date",":k:chanss_f:chan_ts",			" :d:dmy:0: "," chan_ts"] },
	{ f:["Extension",":k:chanss_f:usr",			" %0"," usr"] },
	{ f:["Last Call",":k:chanss_f:last_call",		" %0"," last_call"] },
	{ f:["End Time",":k:chanss_f:state_hangup",		" %0"," state_hangup"] },
	{ f:["Duration",":k:chanss_f:available",		" %0"," available"] },
	{ f:["Occupied",":k:chanss_f:occupied",			" %0"," occupied"] },
	{ f:["Occupancy",":k:chanss_f:occupancy",		" %0"," occupancy"] },
	// todo: adherance
	{ div:["e"] }
]};

te["chanss_f"] = { div:["w70 ma bd sh__ y gw"], c: // "vddvw"], ev:["_undd"
[
	{ s:["x20 yy b bb_","Filters"] },
	{ div:["x15 tt b20"], c:
	[
		{ div:["xx yy"], kf_d:["Date"," :d:dmy:0: ","chan_ts",":k:chanss_f:chan_ts","chan_ts",":k:chanss_f:chan_ts"] },
		{ div:["xx yy"], kf_s:["Extension","usr",":k:chanss_f:usr"] },
		{ div:["xx yy"], kf_s:["Last Call","last_call",":k:chanss_f:last_call"] },
		{ div:["xx yy"], kf_s:["End Time","state_hangup",":k:chanss_f:state_hangup"] },
		{ div:["xx yy"], kf_s:["Duration","available",":k:chanss_f:available"] },
		{ div:["xx yy"], kf_s:["Occupied","occupied",":k:chanss_f:occupied"] },
		{ div:["xx yy"], kf_s:["Occupancy","occupancy",":k:chanss_f:occupancy"] },
	]},
	{ div:["x20 yy"], c:
	[
		{ div:["c w06 r02"], c:[ { ac:["ad btn","chanss_f_tags-chanss_f","_applyf","x y w05 gbl bd ba_br cw tc","Apply"] }, { s:["y07 bd b savl","..."] } ] },
		{ div:["c l20","va"], ac:["ay","","_vpclose","x y w05 ba_bl bd tc cbr","Cancel"], c:[ { p:["g","o"], arg:["",".id",""] } ] },
		{ div:["e"] }
	]}
]};

// --------------------------------------------------------------------

te["chanss_footer"] = { div:["gw mtn08 bt"], c:
[
	{ div:["d y07"], pg:["pgto","chanss_list-chanss"," dh","da dl","chanss_list-chanss"," dh","da dr"] },
	{ div:["e"] }
]};

te["chanss_r"] = { li:["w160 gw","chanss_vw_id-chanss"], ev:["_nnvp"], c:
[
	{ div:["c w15"], s:["x y ",":d:dmyhn:1: "] },
	{ div:["c w10"], s:["x y ","%2"] },
	{ div:["c w10"], s:["x y ",":d:hn:4: "] },
	{ div:["c w10"], s:["x y ",":d:hn:3: "] },
	{ div:["c w10"], s:["x y tr",":h:ms:7:"] },
	{ div:["c w10"], s:["x y tr",":h:ms:5:"] },
	{ div:["c w10"], s:["x y tr",""], c:[ { s:["d","%"] }, { s:["d","%6"] }, { div:["e"] } ] },
	{ div:["e"] } 
]};

te["chanss_k"] = { div:["w160 bt bb"], s:["",""], c: // activate filter ctx
[
	{ k_a:["c w15","call_rr-calls","cd","Date","da db","chan_ts",":k:chanss_k:chan_ts:2"] },
	{ k_a:["c w10","call_rr-calls","cd","Extension","da db","usr",":k:chanss_k:usr:2"] },
	{ k_a:["c w10","call_rr-calls","cd","Last Call","da db","last_call",":k:chanss_k:last_call:2"] },
	{ k_a:["c w10","call_rr-calls","cd","End Time","da db","state_hangup",":k:chanss_k:state_hangup:2"] },
	{ k_a:["c w10","call_rr-calls","cd","Duration","da db","available",":k:chanss_k:available:2"] },
	{ k_a:["c w10","call_rr-calls","cd","Occupied","da db","occupied",":k:chanss_k:occupied:2"] },
	{ k_a:["c w10","call_rr-calls","cd","Occupancy","da db","occupancy",":k:chanss_k:occupancy:2"] },
	{ k_a:["c w10","call_rr-calls","cd","Adherance","da db","adherance",":k:chanss_k:adherance:2"] },
	{ k_a:["c w10","call_rr-calls","cd","Shift Start","da db","shift_start",":k:chanss_k:shift:2"] },
	{ k_a:["c w10","call_rr-calls","cd","Shift End","da db","shift_end",":k:chanss_k:shift:2"] },
	{ div:["e"] }
]};

te["chanss_nb"] = { div:[], c:[ { u:["nb","chanss_nb"] }, { div:["e"] } ] };

te["chanss_title"] = { div:[] }; 

te["chanss_list"] = { list:["chanss_title","chanss_nb","bl br gw oh","chanss_k","chanss_r","chanss","chanss_footer"] },

te["chanss_main"] = { c:
[
	{ div:["tt","vb"], c:
	[
		{ div:["c t"], c:
		[
			{ arg:["","","0"] },
			{ input:["g","","chanss_t","0","radio","1"] },
			{ ac:["","chanss_list-chanss","_tab","x y03 cb b n","Agent Availability"] }, 
		]},
		/*{ div:["d l15 t bb aa"], ac:["","chanss","_csv","x cd s",""], c:
		[ 
			{ div:["c t04"], c:[ { img:["","","/voiceapps/images/download.png", "16"] } ] },
			{ div:["c x y","","CSV"] }, 
			{ div:["e"] }
		]},*/
		{ div:["d l15 t bb","chanss_rpt-chanss-@:1:"], c: // loaded only when tab contents are blank
		[
			{ arg:["","","0"] },
			{ input:["g","","chanss_t","1","radio"] },
			{ ac:["c aa","chanss_rpt_main","_tab","x cd s",""], c:
			[
				{ div:["c t04"], c:[ { img:["","","/voiceapps/images/chart.png", "16"] } ] },
				{ div:["c x y","","Reports"] }, 
				{ div:["e"] }
			]},
			// { div:["d"], ac:["aa","","_dsdd","x02 t04 b02",""],  c:[ { div:["h02 w02 awb"] } ] },
			{ div:["e"] }
		]},
		{ div:["d l15 t bb",""], c: // loaded only when tab contents are blank
		[
			{ arg:["","","0"] },
			{ input:["g","","chanss_t","0","radio"] },
			{ ac:["c aa","chanss_list-chanss","_tab","x cd s",""], c:
			[
				{ div:["c t04"], c:[ { img:["","","/voiceapps/images/list.png", "16"] } ] },
				{ div:["c x y","","List"] }, 
				{ div:["e"] }
			]},
			// { div:["d"], ac:["aa","","_dsdd","x02 t04 b02",""],  c:[ { div:["h02 w02 awb"] } ] },
			{ div:["e"] }
		]},
		{ div:["d t aa bb"], ac:["","chanss_f-chanss_f","_vpf","x cd s",""], c:
		[ 
			{ div:["c t04"], c:[ { img:["","","/voiceapps/images/filter.png", "16"] } ] },
			{ div:["c x y","","Filter"] }, 
			{ div:["e"] }
		]},
		{ div:["e"], c:[ { arg:["","","chanss_list-chanss"] }, { arg:["","","0"] }, { arg:["","","0"] } ] }
	]},
	{ div:["","vf"] },
	{ div:[""], c:
	[
		{ div:[], c:[ { input:["g","","chanss_mv","0","radio","1"] }, { p:["tabv","vt"], chanss_list:[] } ] },
		{ div:[], c:[ { input:["g","","chanss_mv","1","radio"] }, { p:["tabv","vt"] } ] },	// reports			
	]}
]};

