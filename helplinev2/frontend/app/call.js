
rk["call_metrics"] = ["call_count","call_percent"];
re["call_metrics"] = 
{
"call_count":	["call_count",		"Count","0","call_rpt_count","call_rpt-calls-@:1:0:0"],
"call_percent":	["call_percent",	"Percent","1","call_rpt_percent","call_rpt-calls-@:1:1:1"],

}; 

re["call_k"] = 
{
	"vector":["vector","Direction"],
	"user_name":["user_name","Extension"],
	"hangup_status_txt":["hangup_status_txt","Hangup Status"],
	"sla_wait_band":["sla_wait_band","SLA Band"],
	"dispositions^disposition":["dispositions^disposition","Disposition"],
	/*
	"cat_0":["cat_0","Main Category"],
	"cat_1":["cat_1","SubCategory 1"],
	"cat_2":["cat_2","SubCategory 2"],
	"cat_3":["cat_3","SubCategory 3"],
        "cat_4":["cat_3","SubCategory 4"],
        "gbv_related":["gbv_related","GBV Related"],
	"src":["src","Case Source"],
	"priority":["priority","Priority"],
	"status":["status","Status"],
	"created_by":["created_by","Created By"],
	"escalated_to":["escalated_to","Escalated To"],
	"escalated_by":["escalated_by","Escalated By"],
	"assessment":["assessment","Case Assessment"],
	"justice":["justice","Status in Justice System"],
*/
	"dispositions^reporter_age_group":["dispositions^reporter_age_group","Reporter Age Group"],
	"dispositions^reporter_sex":["dispositions^reporter_sex","Reporter Sex"],
	"dispositions^reporter_national_id_type":["dispositions^reporter_national_id_type","Reporter ID Type"],
	"dispositions^reporter_nationality":["dispositions^reporter_nationality","Reporter Nationality"],
	"dispositions^reporter_lang":["dispositions^reporter_lang","Reporter Language"],
	"dispositions^reporter_tribe":["dispositions^reporter_tribe","Reporter Tribe"],
	"dispositions^reporter_location_0":["dispositions^reporter_location_0","Reporter Region"], 
	"dispositions^reporter_location_1":["dispositions^reporter_location_1","Reporter District"],
	"dispositions^reporter_location_2":["dispositions^reporter_location_2","Reporter County"],
	"dispositions^reporter_location_3":["dispositions^reporter_location_3","Reporter Sub County"],
	"dispositions^reporter_location_4":["dispositions^reporter_location_4","Reporter Parish"],
	"dispositions^reporter_location_5":["dispositions^reporter_location_5","Reporter Village"],
	"dispositions^reporter_location_6":["dispositions^reporter_location_6","Reporter Constituency"],
};

rk["call_reporters_k"] = [
"dispositions^reporter_age_group", 		"dispositions^reporter_sex", 
"dispositions^reporter_national_id_type", 	"dispositions^reporter_nationality", 
"dispositions^reporter_lang", 			"dispositions^reporter_tribe", 
"dispositions^reporter_location_0", 		"dispositions^reporter_location_1", 
"dispositions^reporter_location_2", 		"dispositions^reporter_location_3", 
"dispositions^reporter_location_4", 		"dispositions^reporter_location_5",
"dispositions^reporter_location_6"];
re["call_reporters_k"] = re["call_k"];

rk["call_cases_k"] = []; //[ "cat_0", "cat_1", "cat_2", "cat_3", "cat_4", "gbv_related", "src", "priority", "status", "created_by", "escalated_to", "escalated_by", "assessment", "justice"];
re["call_cases_k"] = re["call_k"];

rk["call_calls_k"] = ["vector","user_name","hangup_status_txt","sla_wait_band","dispositions^disposition"];
re["call_calls_k"] = re["call_k"];

// ---

te["call_rpt_metric_tab"] = { div:["c x","%4"], c:
[
	{ arg:["","","0"] },
	{ input:["g","","call_metric","%2","radio","%9"] },
	{ li:["opth x y tc cb","%3","%1"], ev:["_tab"] }
]};

te["call_k_tag"] = { "rpt_axis_tag":["::call_k:0:1","xaxis"] };

te["call_k_r"] = { "rpt_axis_r":["xaxis","call_k_tag","::call_k:0:1"] };

te["call_rpt_ymenu"] = { c:
[
	{ div:["xx t bb_","vb"], c:
	[
		{ div:["c x"], c:[ { input:["g","","call_rpt_vw_t","0","radio","1"] }, { ac:["ay tabu","","_tab","xx y cb","Call"] } ] },
		//{ div:["c x"], c:[ { input:["g","","call_rpt_vw_t","1","radio"] }, { ac:["ay tabu","","_tab","xx y cb","Case"] } ] },
		{ div:["c x"], c:[ { input:["g","","call_rpt_vw_t","2","radio"] }, { ac:["ay tabu","","_tab","xx y cb","Reporter"] } ] },
		{ div:["e"] }
	]},
	{ div:["xx yy"], c:
	[
		{ div:[], c:[ { input:["g","","call_rpt_vw_tv","0","radio","1"] }, { div:["tabv"], uchk:["call_k_r",null,"call_calls_k"] } ] },
		{ div:[], c:[ { input:["g","","call_rpt_vw_tv","1","radio"] }, { div:["tabv"], uchk:["call_k_r",null,"call_cases_k"] } ] },
		{ div:[], c:[ { input:["g","","call_rpt_vw_tv","2","radio"] }, { div:["tabv"], uchk:["call_k_r",null,"call_reporters_k"] } ] },
		//{ div:[], c:[ { input:["g","","call_rpt_vw_tv","3","radio"] }, { div:["tabv"], uchk:["call_k_r",null,"call_clients_k"] } ] },
		//{ div:[], c:[ { input:["g","","call_rpt_vw_tv","3","radio"] }, { div:["tabv"], uchk:["call_k_r",null,"call_perps_k"] } ] },
		//{ div:[], c:[ { input:["g","","call_rpt_vw_tv","4","radio"] }, { div:["tabv"], uchk:["call_k_r",null,"call_services_k"] } ] },
		//{ div:[], c:[ { input:["g","","call_rpt_vw_tv","5","radio"] }, { div:["tabv"], uchk:["call_k_r",null,"call_referals_k"] } ] }
	]}
]};

te["call_rpt_options"] = {  c:
[
	
	{ input:["g","","type","bar","radio","1"] },
	{ ac:["r ay","","_rpt_opt","xx y02 cb",""], c:
	[
		{ div:["c w01_ t"], s:["opt",""] },
		{ s:["c x y ","Bar Chart"] },
		{ div:["e"] }			
	]},
	{ input:["g","","type","line","radio"] },
	{ ac:["r ay","","_rpt_opt","xx y02 cb",""], c:
	[
		{ div:["c w01_ t"], s:["opt",""] },
		{ s:["c x y ","Line Chart"] },
		{ div:["e"] }			
	]},

	{ input:["g","","stacked","stacked","checkbox","1"] },
	{ ac:["r ay","","_rpt_chk","xx y02 cb",""], c:
	[
		{ div:["c w01_ t"], s:["chk",""] },
		{ s:["c x y ","Stacked"] },
		{ div:["e"] }			
	]},

	{ input:["g","","sortrpt","1","checkbox"] },
	{ ac:["r ay","","_rpt_chk","xx y02 cb",""], c:
	[
		{ div:["c w01_ t"], s:["chk",""] },
		{ s:["c x y ","Sort by Total"] },
		{ div:["e"] }			
	]},
]};

te["call_rpt_"] = { c:
[
	{ form:["tt","vrpt"], c:
	[
		{ div:["c"], c:
		[
			{ div:["ay","va"], ac:["","","_dd","x y04 cb",""], c:
			[
				{ s:["c x b h3",null] },
				//{ div:["c"], s:["h02 w02 awb",""] },
				{ div:["e"] }
			]},
			{ div:["dd w20 y ba gw sh","vdd"], ev:["_undd"], c:
			[
				// metrics
			]}	
		]},
		{ div:["d"], c:
		[
			{ div:["ay l20","va"], ac:["","","_dd","x y04 h02 cb ba",""], c:
			[
				{ s:["c x","Options"] },
				{ s:["c x t02 micon","more_vert"] },
				{ div:["e"] }
			]},
			{ div:["dd w18 mln7 mt y ba gw sh","vdd"], ev:["_undd"], call_rpt_options:[] }
		]},
		{ div:["d"], s:["",""], c:
		[
			{ div:["d"], c: // xaxis
			[
				{ div:["ba","va"], s:["",""], c:
				[	
					{ div:["d w03"], ac:["ay","","_dd","x y04",""],  c:[ { div:["h02 w02 awb"] } ] },
					{ div:["e"] }
				]},
				{ div:["dd y mln47 w50 gw ba mt1","vdd_rpt"], ev:["_undd"], c:[ { call_rpt_ymenu:[null,null,null] } ] }
			]},
			{ div:["d"], uchk:["call_k_tag",null] },
			{ s:["d l20 r05 y07 cd","Y Axis:"] },
			{ div:[] },
		]},
		{ div:["d"], s:["",""], c:
		[
			{ uchk:["rpt_dist_r",null,"dist"]}, // xaxis (distribution options)
			{ s:["d l20 r05 y07 cd","X Axis:"] },
			{ div:["e"] },
		]},
		{ div:["e"], c:
		[ 
			{ arg:["","metrics",null] },
			{ input:["g","","rpt",null,"checkbox","1"] },
		]}
	]},
	{ div:["","call_rpt_vw-calls"], urpt:[] } 
]};

te["call_rpt"] = { call_rpt_:["::call_metrics:4:1","%2","%2","%3","%4","%7"] };  
te["call_rpt_percent"] = { call_rpt_:["Percent", "hangup_status_txt","hangup_status_txt","hangup_status_txt", "hangup_status_txt", "-", "call_percent","call_percent"] };
te["call_rpt_count"] = { call_rpt_:["Count", "hangup_status_txt","hangup_status_txt","hangup_status_txt", "hangup_status_txt", "-", "call_count","call_count"] };

te["call_rpt_main"] = { c:
[
	{ div:["g xx t15 bb_ s","vb"], c:
	[
		{ s:["c x y cd","Metric:"] },
		// { uchk:["call_rpt_metric_tab","call_count","call_metrics"] },
		// + add // todo add mutiple metrics to same canvas // then multi-metric with from different resources
		{ div:["d g"], c:
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
		{ div:[], c:[ { input:["g","","call_rptv","0","radio","1"] }, { p:["tabv","vt"], call_rpt_count:[] } ]},
		{ div:[], c:[ { input:["g","","call_rptv","0","radio"] }, { p:["tabv oh","vt"] } ] },
		{ div:[], c:[ { input:["g","","call_rptv","0","radio"] }, { p:["tabv","vt"] } ] },
		{ div:[], c:[ { input:["g","","call_rptv","0","radio"] }, { p:["tabv","vt"] } ] },
		{ div:[], c:[ { input:["g","","call_rptv","0","radio"] }, { p:["tabv","vt"] } ] },
		{ div:[], c:[ { input:["g","","call_rptv","0","radio"] }, { p:["tabv","vt"] } ] },
		{ div:[], c:[ { input:["g","","call_rptv","0","radio"] }, { p:["tabv","vt"] } ] },
		{ div:[], c:[ { input:["g","","call_rptv","0","radio"] }, { p:["tabv","vt"] } ] },
	]}
]};

// ---------------------------------------------------------------------------------------------

te["call_case_none"] = { div:[], c:
[
	{ ac:["c xx yy ao","activity_popup-r_","_vp","w24 yy gb bd_",""], c:
	[
		{ s:["c xx y n cw","Select Reporter"] },
		{ div:["d l20 t"], s:["h02 w02 awR",""] },
		{ div:["e"], c:[ { arg:["task_chan-43","","%9"] }, { arg:["uniqueid-10","","%10"] }, { arg:["phone-11","","%12"] }, { arg:["vector-12","","%14"] } ] }
		// call
	]},
	{ div:["e"] }
]};

te["call_case"] = { ufn:["ufn_vw","call_case_","call_case_none"] };

// ---------------------------------------------------------------------------------------------

te["call_vw_id_qa_score"] = { c:
[
	{ s:["d xx y tr gws h02 bd8 b",""], c:[ { s:["d"," %"] }, { s:["d",":v:calls:qa_score"] }, { div:["e"] } ] },
	{ s:["d x y h02","QA Score"] },
	{ div:["e"] }
]};

te["call_vw_id_ssqa_form"] = { c: // todo: show only for supervisor
[
 	{ ac:["ay ","","","xx y tr bd8","Open QA Form"] }
]};

te["call_vw_id_qa_form"] = { div:[], c:
[
	{ ac:["","qa_form-r_-^","_vp","xx y tr bd8",""], c:
	[
		{ s:["tr","Open QA"] }, 
		{ div:[], c:[ { arg:["chan_uniqueid-5","","%0"] }, { arg:["chan_ts-6","",":v:calls:chan_ts"] }, { arg:["chan_vector-7","",":v:calls:vector"] }, { arg:["chan_phone-8","",":v:calls:phone"] }, { arg:["chan_usr-9","",":v:calls:usr"] }, { arg:["chan_talk_time-11","",":v:calls:talk_time"] } ] },
	]},
	{ div:["g"], arg:["","","call_r_-r_-va--@"] }
]};


te["call_vw_id_qa"] = { u:[":u::30:0:call_vw_id_qa_form:call_vw_id_qa_score"] };

te["call_vw_id_play"] = { div:["gws bd8"], c:
[
	{ ac:["ay","vfile_vw_r-calls-va-play","_u"," bd8 y cb",""], c:
	[ 
		{ s:["c w02 x h3_ micon","play_arrow"] },
		{ s:["c y02","Talk Time"] },
		{ s:["d xx y02",":h:ms:11:"] },	// ":v:calls:talk_time:h:ms::"
		{ div:["e"], c:[ { arg:["",".id","%0"] }, { arg:["","file","wav"] } ] },
	]},
	{ p:["","play"] }
]};

te["call_vw_id"] = { div:["w70 ma sh__ y gw_","vddvw"], ev:["_undd"], c:
[
	{ div:["x20 yy"], c:
	[
		{ s:["c x tt h3 b","Call Details"] },
		{ ac:["d ab","","_uvp","x cb",""], c:[ { s:["c h2 t03","&Cross;"] }, { s:["c x y g","Close"] }, { div:["e"] } ] },
		// { div:["d xx ay","va"], ac:["r05","client_ed-clients-vp","_u","xx y gww cb bd","Edit"], c:[ { arg:["",".id","%0"] } ] },
		{ div:["e"] }
	]},
	{ div:["x20"], c:
	[ 
		{ div:["d xx w30"], s:["abs tt w30",""], c:
		[
			{ div:["","va"], usub:["call_vw_id_play,call_vw_id_play","r_",":v:calls:hangup_status_txt","answered,voicemail"] }, 
			{ div:["yy","va"], usub:["call_vw_id_qa","r_",":v:calls:hangup_status_txt","answered"] }
		]},
		{ div:["e"] }
	]},
	{ div:["x20 y"], c:
	[
		{ p:["c","nb"], c:[ { u:["nb","calls_nb"] }, { u:["nb","errors"] } ] },
		{ div:["e"] }
	]},
	{ div:["x20"], c:
	[ 
		{ s:["c w10 x y cd","Call Date"] }, 
		{ s:["c w30 x y cb",":d:dmyhnr:1: "] }, 
		{ div:["e"] }
	]},
	{ div:["x20 t15"], c:
	[ 
		{ s:["c w10 x y cd","Direction"] }, 
		{ s:["c w30 x y cb",":v:calls:vector::vector:1"] }, 
		{ div:["e"] }
	]},
	{ div:["x20 t15"], c:
	[ 
		{ s:["c w10 x y cd","Phone"] }, 
		{ s:["c w30 x y cb",":v:calls:phone"] }, 
		{ div:["e"] }
	]},
	{ div:["x20 t15"], c:
	[ 
		{ s:["c w10 x y cd","Extension"] },
		{ s:["c x",":v:calls:usr"] },
		{ s:["c x",":v:calls:user_name"] }, 
		{ div:["e"] }
	]},
	{ div:["x20 t15"], c:
	[ 
		{ s:["c w10 x y cd","Wait Time"] }, 
		{ s:["c w30 x y cb",":h:ms:10:"] }, // :h:ms:10:
		{ div:["e"] }
	]},
	{ div:["x20 t15"], c:
	[ 
		{ s:["c w10 x y cd","Talk Time"] }, 
		{ s:["c w30 x y cb",":h:ms:11:"] }, 
		{ div:["e"] }
	]},
	{ div:["x20 t15"], c:
	[ 
		{ s:["c w10 x y cd","Hangup Status"] }, 
		{ s:["c w30 x y cb",":v:calls:hangup_status_txt"] }, 
		{ div:["e"] }
	]},
	{ div:["x20 t15"], c:
	[ 
		{ s:["c w10 x y cd","Disposition"] }, 
		{ s:["c w30 x y cb",":v:calls:dispositions"] }, 
		{ div:["e"] }
	]},
	{ div:["x20 t15 b25"], c:
	[ 
		{ s:["c w10 x y cd","Reporter"] }, 
		{ s:["c w30 x y cb",":v:calls:contacts"] }, 
		{ div:["e"] }
	]},

]};

// ---------------------------------------------------------------------------------------------

te["call_lst_footer"] = { div:["y"], c:
[	
	{ div:["d cd"], pg:["pgto","call_lst-calls"," dh","da dl_","call_lst-calls"," dh","da dr_"] },
	{ div:["e"] }
]};

te["call_lst_r"] = { li:["xx yy ah gw bb_",""],  c:
[

	{ div:[""], c:
	[ 
		// { s:["c x y","::vector:22:2"] },  // c x y cb gws h01 w01 cb bd16
		{ s:["c x y  cb","::vector:22:6"] }, 
		{ s:["c y","::vector:22:4"] }, 
		{ s:["c x y cb","%5"] },
		{ s:["c x y cd","::vector:22:5"] }, 
		{ s:["c x y","::branch:25:1"] },
		// { s:["c y cb","Extension"] },
		{ s:["c y cb","%6"] },
		{ div:["c xx y02"], s:["::hangup_status:13:3","::hangup_status:13:2"] },
		//{ s:["c ll cd","Wait Time:"] },
		//{ s:["c x ",":h:ms:10:"] },
		{ s:["c y cd","Talk Time:"] },
		{ s:["c x y ",":h:ms:11:"] },
		{ s:["d x y",":r::1:: : ago:: : ago:"] },
		//{ s:["d x y cd","%5"] },
		{ div:["e"] } 
	]}, 
	{ div:["g"], c:
	[
		{ s:["c l25","%13"] },
		//{ s:["c ll cd","Wait Time:"] },
		//{ s:["c x ",":h:ms:10:"] },
		{ s:["c l cd","Talk Time:"] },
		{ s:["c x ",":h:ms:11:"] },
		//{ s:["c l cd","Hold Time:"] },
		//{ s:["c x ",":h:ms:28:"] },
		// { s:["d x cd s","%5"] },
		{ div:["e"] }
	]},
]};

te["call_lst_k"] = { div:["x20 gws bb_"], s:["w160",""], c: // activate filter ctx
[
	{ k_a:["c w13","call_rr-calls","cb b","Date","da db","chan_ts",":k:calls_k:chan_ts:2"] },
	{ k_a:["c w10","call_rr-calls","cb b","Direction","da db","vector",":k:calls_k:vector:2"] },
	{ k_a:["c w10","call_rr-calls","cb b","Branch","da db","branch",":k:calls_k:branch:2"] },
	//{ k_a:["c w10","call_rr-calls","","Trunk DID","da db","trunk",":k:calls_k:trunk:2"] },
	{ k_a:["c w13","call_rr-calls","cb b","Phone","da db","phone",":k:calls_k:phone:2"] },
	{ k_a:["c w10","call_rr-calls","cb b","Extension","da db","usr",":k:calls_k:usr:2"] },
	{ k_a:["c w10","call_rr-calls","w08 tr cb b","Wait Time","da db","wait_time_tot",":k:calls_k:wait_time_tot:2"] },
	{ k_a:["c w10","call_rr-calls","w08 tr cb b","Talk Time","da db","talk_time",":k:calls_k:talk_time:2"] },
	{ k_a:["c w13","call_rr-calls","w11 tr cb b","Hangup By","da db","hangup_reason",":k:calls_k:hangup_reason:2"] },
	{ k_a:["c w13","call_rr-calls","w11 tr cb b","Hangup Status","da db","hangup_status",":k:calls_k:hangup_status:2"] },
	{ k_a:["c w15","call_rr-calls","w13 tr cb b","Disposition","da db","category",":k:calls_k:category:2"] },
	{ k_a:["c w10","call_rr-calls","w08 tr cb b","QA Result","da db","qa_score",":k:calls_k:qa_score:2"] },
	{ div:["e"] }
]};

te["call_lst_nb"] = { div:[], c:[ { u:["nb","calls_nb"] }, { div:["e"] } ] };

te["call_lst_title"] = { div:["bb_","va"], c:
[
	{ div:["c x y","va"], ac:["","call_lst-calls-vt","_u","x y cb b","Call History"], c:[ { arg:["","phone",":k:calls_k:phone:2"] } ] },
	{ div:["e"] }
]};

te["call_lst"] = { list:["call_lst_title","call_lst_nb","","noop","call_lst_r","calls","call_lst_footer"] },

// ----------------------------------------------

te["call_f_tags_"] = { c: 
[
	{ f:["Date",null,		" :d:dmy:0: ","chan_ts"," "] },
	{ f:["Direction",null,		" ::vector:0:1","vector"," "] },
	{ f:["Phone",null,		" %0","phone"," "] },
	// { f:["Extension",null,	" %0","usr"," "] },
	{ f:["Extension",null,		" %1","user_id"," %1"] },
	{ f:["Wait Time",null,		" %0","wait_time_tot"," "] },
	{ f:["Talk Time",null,		" %0","talk_time"," "] },
	{ f:["Hold Time",null,		" %0","hold_time"," "] },
	{ f:["Hangup By",null,		" ::hangup_reason:0:1","hangup_reason"," "] },
	{ f:["Hangup Status",null,	" ::hangup_status:0:1","hangup_status_txt"," "] },
	{ f:["Disposition",null,	" %1","dispositions^disposition_id"," %1"] },
	{ f:["QA Done",null,		" ::qa_done:0:1","qa_done"," "] },

	{ f:["Case ID",null,		" %0","dispositions^case_id"," "] },
	
	{ f:["Reporter Name",null,	" %0","dispositions^reporter_fullname",""] },
	{ f:["Reporter Phone",null,	" %0","dispositions^reporter_phone",""] },
	{ f:["Reporter Age",null,	" %1","dispositions^reporter_age_group_id"," %1"] },
	{ f:["Reporter Gender",null,	" %1","dispositions^reporter_sex_id"," %1"] },
	{ f:["Reporter Location",null,	" %1","dispositions^reporter_location_id"," %1"] },
	{ f:["Reporter ID Type",null,	" %1","dispositions^reporter_national_id_type_id"," %1"] },
	{ f:["Reporter Nationality",null," %1","dispositions^reporter_nationality_id"," %1"] },
	{ f:["Reporter Language",null,	" %1","dispositions^reporter_lang_id"," %1"] },
	{ f:["Reporter Tribe",null,	" %1","dispositions^reporter_tribe_id"," %1"] },	

	//{ p:["g","o"], arg:["","_title",null] }, 
	{ div:["e"] }
]};


te["call_f_tags"] = { call_f_tags_:[":k:calls_f:chan_ts", ":k:calls_f:vector", ":k:calls_f:phone", ":k:calls_f:user_id", 
":k:calls_f:wait_time_tot", ":k:calls_f:hold_time", ":k:calls_f:talk_time", 
":k:calls_f:hangup_reason",":k:calls_f:hangup_status_txt", 
":k:calls_f:dispositions^disposition_id", 
":k:calls_f:qa_done",

":k:calls_f:dispositions^case_id",

":k:calls_f:dispositions^reporter_fullname", 		":k:calls_f:dispositions^reporter_phone", 
":k:calls_f:dispositions^reporter_age_group_id", 	":k:calls_f:dispositions^reporter_sex_id", 
":k:calls_f:dispositions^reporter_location_id",
":k:calls_f:dispositions^reporter_national_id_type_id", ":k:calls_f:dispositions^reporter_nationality_id", 
":k:calls_f:dispositions^reporter_lang_id",		":k:calls_f:dispositions^reporter_tribe_id"] };


te["call_f_tags_k"] = { call_f_tags_:[":k:calls_k:chan_ts:2", ":k:calls_k:vector:2", ":k:calls_k:phone:2", ":k:calls_k:user_id:2", 
":k:calls_k:wait_time_tot:2", ":k:calls_k:talk_time:2", ":k:calls_k:hold_time:2", 
":k:calls_k:hangup_reason:2", ":k:calls_k:hangup_status_txt:2", 
":k:calls_k:dispositions^disposition_id:2", 
":k:calls_k:qa_done:2",

":k:calls_k:dispositions^case_id:2", 

":k:calls_k:dispositions^reporter_fullname:2", 		":k:calls_k:dispositions^reporter_phone:2", 
":k:calls_k:dispositions^reporter_age_group_id:2", 	":k:calls_k:dispositions^reporter_sex_id:2", 
":k:calls_k:dispositions^reporter_location_id:2",
":k:calls_k:dispositions^reporter_national_id_type_id:2", ":k:calls_k:dispositions^reporter_nationality_id:2", 
":k:calls_k:dispositions^reporter_lang_id:2", 		":k:calls_k:dispositions^reporter_tribe_id:2"] };


te["call_reporters_f"] = { c:
[
	{ div:["xx yy"], kf_s:["Name","dispositions^reporter_fullname",":k:calls_f:dispositions^reporter_fullname"] },

	{ div:["xx yy"], kf_s:["Phone","dispositions^reporter_phone",":k:calls_f:dispositions^reporter_phone"] },

	{ div:["xx yy"], kf_l:["Age","tag_-r_--o--%1-category_id-dispositions^reporter_age_group_id-%0-%1", "case_lc_main-subcategories", 
":k:calls_f:dispositions^reporter_age_group_id", ""," %1","category_id","dispositions^reporter_age_group_id"," %0"," %1", "case_age_group_root_id"] },

	{ div:["xx yy"], kf_l:["Sex","tag_-r_--o--%1-category_id-dispositions^reporter_sex_id-%0-%1", "case_lc_main-subcategories",  
":k:calls_f:dispositions^reporter_sex_id", ""," %1","category_id","dispositions^reporter_sex_id"," %0"," %1", "case_sex_root_id"] },

	{ div:["xx yy"], kf_l:["Location","tag_-r_--o--%1-category_id-dispositions^reporter_location_id-%0-%1", "case_location_lc_main-subcategories",  ":k:calls_f:dispositions^reporter_location_id", ""," %1","category_id","dispositions^reporter_location_id"," %0"," %1", "case_location_root_id"] },

	{ div:["xx yy"], kf_l:["ID Type","tag_-r_--o--%1-category_id-dispositions^reporter_national_id_type_id-%0-%1", "case_lc_main-subcategories",  ":k:calls_f:dispositions^reporter_national_id_type_id", ""," %1","category_id","dispositions^reporter_national_id_type_id"," %0"," %1", "case_national_id_type_root_id"] },

	{ div:["xx yy"], kf_l:["Nationality","tag_-r_--o--%1-category_id-dispositions^reporter_nationality_id-%0-%1", "case_lc_main-subcategories",  ":k:calls_f:dispositions^reporter_nationality_id", ""," %1","category_id","dispositions^reporter_nationality_id"," %0"," %1", "case_nationality_root_id"] },

	{ div:["xx yy"], kf_l:["Language","tag_-r_--o--%1-category_id-dispositions^reporter_lang_id-%0-%1", "case_lc_main-subcategories",  ":k:calls_f:dispositions^reporter_lang_id", ""," %1","category_id","dispositions^reporter_lang_id"," %0"," %1", "case_lang_root_id"] },

	{ div:["xx yy"], kf_l:["Tribe","tag_-r_--o--%1-category_id-dispositions^reporter_tribe_id-%0-%1", "case_lc_main-subcategories",  ":k:calls_f:dispositions^reporter_tribe_id", ""," %1","category_id","dispositions^reporter_tribe_id"," %0"," %1", "case_tribe_root_id"] },

]};

te["call_cases_f"] = { c:
[
	{ div:["xx yy"], kf_s:["CaseID","dispositions^case_id",":k:calls_f:dispositions^case_id"] },						
			
	/* 
	{ div:["xx yy"], kf_d:["Created On"," :d:dmy:0: ","created_on",":k:calls_f:created_on","created_on",":k:calls_f:created_on"] },
			
	{ div:["xx yy"], kf_l:["Created By","tag_-r_--o--%5-user_id-created_by_id-%0-%5",   "user_lc_main-users",":k:calls_f:created_by_id", 
""," %1","user_id","created_by_id"," %0"," %1",  "noop"] },

	{ div:["xx yy"], kf_c:["Source","tag_-r_--o--::case_src:0:1--src-%0-",  	":k:calls_f:src",
""," %0","","src"," %0","", 				":k:calls_f:src","case_src", "src"," %0",""] },
		
	{ div:["xx yy"], kf_l:["Category","tag_-r_--o--%1-category_id-case_category_id-%0-%1",   "case_category_lc_main-subcategories",  ":k:calls_f:case_category_id",  ""," %1","category_id","case_category_id"," %0"," %1", "case_category_root_id"] },
	
	{ div:["xx yy"], kf_c:["GBV Related", "tag_-r_--o--::yesno:0:2--gbv_related-%0-",  ":k:calls_f:gbv_related",
""," ::yesno:0:2","","gbv_related"," %0","",       ":k:calls_f:gbv_related","yesno",  "gbv_related"," ::yesno:0:2",""] },

	{ div:["xx yy"], kf_c:["Priority", "tag_-r_--o--::case_priority:0:1--priority-%0-",  ":k:calls_f:priority", 
""," ::case_priority:0:1","","priority"," %0","", 	":k:calls_f:priority","case_priority",  "priority"," ::case_priority:0:1",""] },
				
	{ div:["xx yy"], kf_c:["Status", "tag_-r_--o--::case_status:0:1--status-%0-",  	":k:calls_f:status",
""," ::case_status:0:1","","status"," %0","", 	":k:calls_f:status","case_status",  "status"," ::case_status:0:1",""] },
		
	{ div:["xx yy"], kf_l:["Escalated To","tag_-r_--o--%5-user_id-escalated_to_id-%0-%5",   "user_lc_main-users", ":k:calls_f:escalated_to_id", 
""," %1","user_id","escalated_to_id"," %0"," %1", "noop"] },	
		
	{ div:["xx yy"], kf_l:["Case Assessment","tag_-r_--o--%1-category_id-assessment_id-%0-%1",   "case_lc_main-subcategories", ":k:calls_f:assessment_id", 
""," %1","category_id","assessment_id"," %0"," %1", "case_assessment_root_id"] },	

	{ div:["xx yy"], kf_l:["Status in Justice System","tag_-r_--o--%1-category_id-justice_id-%0-%1",   "case_lc_main-subcategories", ":k:calls_f:justice_id", 
""," %1","category_id","justice_id"," %0"," %1", "case_justice_root_id"] },	
	*/	
				
]};

te["call_calls_f"] = { c:
[
	{ div:["xx yy"], kf_d:["Date"," :d:dmy:0: ","chan_ts",":k:calls_f:chan_ts","chan_ts",":k:calls_f:chan_ts"] },
	{ div:["xx yy"], kf_c:["Direction","tag_-r_--o--::vector:0:1--vector-%0-",  ":k:calls_f:vector",
""," ::vector:0:1","","vector"," %0","", 	":k:calls_f:vector","vector", "vector"," ::vector:0:1"," "] },	
	{ div:["xx yy"], kf_s:["Phone","phone",":k:calls_f:phone"] },
		// { div:["xx yy"], kf_s:["Extension","usr",":k:calls_f:usr"] },
	{ div:["xx yy"], kf_l:["Extension","tag_-r_--o--%5-user_id-user_id-%0-%5",   "user_lc_main-users", ":k:calls_f:user_id", 
""," %1","user_id","user_id"," %0"," %1", "noop"] },
	{ div:["xx yy"], kf_s:["Wait Time","wait_time_tot",":k:calls_f:wait_time_tot"] },
	{ div:["xx yy"], kf_s:["Talk Time","talk_time",":k:calls_f:talk_time"] },
	{ div:["xx yy"], kf_s:["Hold Time","hold_time",":k:calls_f:hold_time"] },
	{ div:["xx yy"], kf_c:["Hangup By","tag_-r_--o--::hangup_reason:0:1--hangup_reason-%0-",  ":k:calls_f:hangup_reason",
""," ::hangup_reason:0:1","","hangup_reason"," %0","", 	":k:calls_f:hangup_reason","hangup_reason", "hangup_reason"," ::hangup_reason:0:1"," "] },	
	{ div:["xx yy"], kf_c:["Hangup Status","tag_-r_--o--::hangup_status:0:1--hangup_status_txt-%0-",  ":k:calls_f:hangup_status_txt",
""," ::hangup_status:0:1","","hangup_status_txt"," %0","", 	":k:calls_f:hangup_status_txt", "hangup_status", "hangup_status_txt"," ::hangup_status:0:1"," "] },
		
	// { div:["xx yy"], kf_s:["CaseID","dispositions^case_id",":k:calls_f:dispositions^case_id"] },			

	{ div:["xx yy"], kf_l:["Disposition","tag_-r_--o--%1-category_id-dispositions^disposition_id-%0-%1", "case_lc_main-subcategories", 
":k:calls_f:dispositions^disposition_id", ""," %1","category_id","dispositions^disposition_id"," %0"," %1", "case_disposition_root_id"] },

	{ div:["xx yy"], kf_c:["QA Done","tag_-r_--o--::qa_done:0:1--qa_done-%0-",  ":k:calls_f:qa_done",
""," ::qa_done:0:1","","qa_done"," %0","", 	":k:calls_f:qa_done","qa_done", "qa_done"," ::qa_done:0:1"," "] },
]};

te["call_f"] = { div:["w55 ma sh__ y gw_","vddvf"], ev:["_undd"], c:
[
	{ s:["x20 t15 n b","Search Call"] },
	{ div:[], c:
	[
		{ div:["xx t15 bb_","vb"], c:
		[
			{ div:["c x"], c:[ { input:["g","","case_f_vw_t","0","radio","1"] }, { ac:["ay tabu","","_tab","xx y cb","Call"] } ] },
			{ div:["c x"], c:[ { input:["g","","case_f_vw_t","1","radio"] }, { ac:["ay tabu","","_tab","xx y cb","Case"] } ] },
			{ div:["c x"], c:[ { input:["g","","case_f_vw_t","2","radio"] }, { ac:["ay tabu","","_tab","xx y cb","Reporter"] } ] },
			// { div:["c x"], c:[ { input:["g","","case_f_vw_t","3","radio"] }, { ac:["ay tabu","","_tab","xx y cb","Client"] } ] },
			// { div:["c x"], c:[ { input:["g","","case_f_vw_t","4","radio"] }, { ac:["ay tabu","","_tab","xx y cb","Perpetrator"] } ] },
			// { div:["c x"], c:[ { input:["g","","case_f_vw_t","5","radio"] }, { ac:["ay tabu","","_tab","xx y cb","Sevices"] } ] },
			// { div:["c x"], c:[ { input:["g","","case_f_vw_t","6","radio"] }, { ac:["ay tabu","","_tab","xx y cb","Referals"] } ] },
			{ div:["e"] }
		]},
		{ div:["x15 tt b20"], c:
		[
			{ div:[], c:[ { input:["g","","case_f_vw_tv","0","radio","1"] }, { div:["tabv"], call_calls_f:[] } ] },
			{ div:[], c:[ { input:["g","","case_f_vw_tv","0","radio"] }, { div:["tabv"], call_cases_f:[] } ] },
			{ div:[], c:[ { input:["g","","case_f_vw_tv","1","radio"] }, { div:["tabv"], call_reporters_f:[] } ] },
			// { div:[], c:[ { input:["g","","case_f_vw_tv","2","radio"] }, { div:["tabv"], call_clients_f:[] } ] },
			// { div:[], c:[ { input:["g","","case_f_vw_tv","3","radio"] }, { div:["tabv"], call_perpetrators_f:[] } ] },
			// { div:[], c:[ { input:["g","","case_f_vw_tv","4","radio"] }, { div:["tabv"], call_services_f:[] } ] },
			// { div:[], c:[ { input:["g","","case_f_vw_tv","5","radio"] }, { div:["tabv"], call_referals_f:[] } ] }
		]}
	]},
	{ p:["g","o"], arg:["","_title",":k:calls_f:_title"] },
	{ vp_apply:["call_f_tags-calls_f"] }
]};

// ------------------------------------------------------------------------------------------------------------------------------------------

te["call_footer"] = { div:["x ba"], c:
[
	{ div:["d y07"], pg:["pgto","call_list-calls"," dh","da dl","call_list-calls"," dh","da dr"] },
	{ div:["e"] }
]};

te["call_r_qa_score"] = { s:["xx t b05 h01_",""], c:
[
	{ s:["c",":v:calls:qa_score"] }, 
	{ s:["c"," %"] },
	{ div:["e"] }
]};

te["call_r_"] = { c:
[
	{ input:["g","","callvwr","1","radio",""] },
	{ li:["ay w300","call_vw_id-calls"], ev:["_vp"], c:
	[
		{ div:["c w17"], s:["xx y08",":d:dmyhnr:1: "] },
		{ div:["c w13"], s:["xx tt b05 h01_",":v:calls:vector::vector:1"] },
		{ div:["c w15"], s:["xx tt b05 h01_",":v:calls:phone"] },
		{ div:["c w15"], s:["tt b05 h01_  xx",""], c:
		[
			{ s:["c",":v:calls:usr"] },
			{ s:["c x",":v:calls:user_name"] },
			{ div:["e"] } 
		]},
	
		{ div:["c w15"], s:["tt b05 h01_  xx",":h:ms:10:"] }, // wait time

		{ div:["c w15"], c:
		[
			{ s:["tt b05 h01_  xx",":h:ms:11:"] },
			// { div:["c w08"], s:["tt b05 h01_  xx tr",":h:ms:30:"] }, // hold time
		]},
		
		{ div:["c w15"], c:
		[
			{ s:[" tt b05 h01_  xx",":v:calls:hangup_status_txt"] },
			// { div:["c w12"], s:["tt b05 h01_  xx tr",":v:calls:hangup_reason::12:1"] },
		]},
		
		{ div:["c w15"], c:
                [
                        { s:[" tt b05 h01_  xx",":v:calls:hangup_reason::hangup_reason:1"] },
                ]},

		{ div:["c w15 t"], u:[":u::30:0:noop:call_r_qa_score"] },
		
		{ div:["c w20 t"], s:["xx t b05 h01_",":v:calls:dispositions"] },
		
		{ div:["c w100 xx y"], s:["",":v:calls:contacts"] },
	
		{ div:["e"], c:[ { arg:["",".id","%0"] } ] }
	]}
]};

te["call_r"] = { li:["w300","va"], call_r_:[] };

te["call_k"] = { div:["w300 bt bb"], s:["",""], c: // activate filter ctx
[
	{ k_a:["c w17","call_rr-calls","cd st","Date","da db","chan_ts",":k:calls_k:chan_ts:2"] },
	{ k_a:["c w13","call_rr-calls","cd st","Direction","da db","vector",":k:calls_k:vector:2"] },
	{ k_a:["c w15","call_rr-calls","cd","Phone","da db","phone",":k:calls_k:phone:2"] },
	{ k_a:["c w15","call_rr-calls","cd","Extension","da db","user_id",":k:calls_k:user_id:2"] },
	{ k_a:["c w15","call_rr-calls","w12 cd ","Wait Time","da db","wait_time_tot",":k:calls_k:wait_time_tot:2"] },
	{ k_a:["c w15","call_rr-calls","w12 cd ","Talk Time","da db","talk_time",":k:calls_k:talk_time:2"] },
	{ k_a:["c w15","call_rr-calls","w12 cd ","Hangup Status","da db","hangup_status_txt",":k:calls_k:hangup_status_txt:2"] },
        { k_a:["c w15","call_rr-calls","w12 cd ","Hangup By","da db","hangup_reason",":k:calls_k:hangup_reason:2"] },
	{ k_a:["c w15","call_rr-calls","w12 cd ","QA Score","da db","qa_done",":k:calls_k:qa_done:2"] },
	{ k_a:["c w20","call_rr-calls","w12 cd ","Disposition","da db","dispositions^disposition_id",":k:calls_k:dispositions^disposition_id:2"] },
	{ k_a:["c w50","call_rr-calls","w12 cd ","Reporter","da db","dispositions^reporter_id",":k:calls_k:dispositions^reporter_id:2"] },	
	
	{ div:["e"], c:
	[
		{ arg:["","dispositions^case_id",		":k:calls_k:dispositions^case_id:2"] },
		{ arg:["","dispositions^reporter_contact_id",	":k:calls_k:dispositions^reporter_contact_id:2"] },
		{ arg:["","dispositions^reporter_fullname",	":k:calls_k:dispositions^reporter_fullname:2"] },
		{ arg:["","dispositions^reporter_phone",	":k:calls_k:dispositions^reporter_phone:2"] },
		{ arg:["","dispositions^reporter_age_group_id",	":k:calls_k:dispositions^reporter_age_group_id:2"] },
		{ arg:["","dispositions^reporter_sex_id",	":k:calls_k:dispositions^reporter_sex_id:2"] },
		{ arg:["","dispositions^reporter_location_id",	":k:calls_k:dispositions^reporter_location_id:2"] },
		{ arg:["","dispositions^reporter_national_id_type_id",":k:calls_k:dispositions^reporter_national_id_type_id:2"] },
		{ arg:["","dispositions^reporter_nationality_id",":k:calls_k:dispositions^reporter_nationality_id:2"] },
		{ arg:["","dispositions^reporter_lang_id",	":k:calls_k:dispositions^reporter_lang_id:2"] },
		{ arg:["","dispositions^reporter_tribe_id",	":k:calls_k:dispositions^reporter_tribe_id:2"] },
	]}
]};

te["call_nb"] = { div:[], c:[ { u:["nb","calls_nb"] }, { div:["e"] } ] };

te["call_title"] = { div:[] }; 

te["call_list"] = { list:["call_title","call_nb","bl br ox","call_k","call_r","calls","call_footer"] };

te["call_main"] = { c:
[
	{ div:["tt","vb"], c:
	[
		{ div:["c t03"], c:
		[
			{ div:["","va"], s:["",""], c:
			[
				{ input:["g","","call_t_","0","radio","1"] },
				{ ac:["c","call_main-calls-vftab","_u","x y cb b h2","Call History"] }, 
				//{ ac:["c t02 x ay","","_dd","h02 w02 gws_ awb",""] },
				{ div:["e"] } //, arg:["","_title","%5"] }
			]},
			{ div:["dd x y gw ba sh nd w14","vdd"], c:
			[
			
			]}
		]},
		
		{ div:["c l40"], c: 
		[
			{ arg:["call_list-calls","","0"] },
			{ input:["g","","calls_t_","0","radio","1"] },
			{ li:["opto x bl bt bb gw s cb","call_list-calls"], ev:["_tab"], c:
			[
				{ s:["c l t h3_ micon","list"] },
				{ div:["c xx y","","List"] }, 
				{ div:["e"] }
			]}
		]},

		{ div:["c"], c: 
		[
			{ arg:["call_rpt_vw-calls-@","","1,0"] },
			{ input:["g","","calls_t_","1","radio"] },
			{ li:["opto x ba gw s cb","call_rpt_main-r_"], ev:["_tab"], c:[ { div:[], c:
			[
				{ s:["c l t h3_ micon","bar_chart"] },
				{ s:["c xx y","Reports"] }, 
				{ div:["e"] }
			]} ]}
		]},

		{ div:["c l40"], ac:["ay","call_f-calls_f","_vpf","x t01 bd_ cb s",""], c:
		[ 
			{ s:["c t04 h3_ micon","search"] },
			{ div:["c x y","","Search"] }, 
			{ div:["e"] }
		]},

		{ div:["c l40"], ac:["ay","calls","_download","x t01 bd_ cb s",""], c:
		[ 
			{ s:["c t04 h3_ micon","download"] },
			{ div:["c x y","","Download"] }, 
			{ div:["e"] }
		]},
		
		{ div:["e"], c:[ { arg:["","","call_list-calls"] }, { arg:["","","0"] }, { arg:["","","-1"] }, { arg:["","",""] } ] }
	]},

	{ div:["yy","vf"], c:[ { div:["","call_f-calls_f"], c: // ev:["_n_vpf"], c:
	[
		{ call_f_tags_k:[] }
	]} ]},

	{ div:[], c:
	[
		{ div:[], c:[ { input:["g","","calls_v","0","radio","1"] }, { p:["tabv yy","vt"], call_list:[] } ] },
		{ div:[], c:[ { input:["g","","calls_v","1","radio"] }, { p:["tabv","vt"] } ] },				
	]}
]};
	
te["calls"] = { c:
[
	{ div:["g"], c:
	[
		
	]},
	{ form:[], c:
	[
		{ div:[], c:
		[	
			{ input:["g","","call_vw_vt","0","radio","1"] }, 
			{ p:["tabv x20 y20 gw mm","vftab"], call_main:[] } 
		]},
		{ div:[], c:
		[	
			{ input:["g","","call_vw_vt","1","radio"] }, 
			{ p:["tabv gw yy mm","vfvw"] }
		]}
	]}
]};

// -----------------------------------------------------------------------------------------------------------------------------

function call_qa_done (r,a)
{
	if (r[11]<=0) return 2; // no talktime
	if (r[36]==1) return 0; //
	return 1;
}


