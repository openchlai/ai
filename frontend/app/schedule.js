

te["campaign_arg_voiceblast"] = { arg:["campaign","","3"] };
te["campaign_arg_outbound"] = { arg:["campaign","","2"] };
te["campaign_arg_inbound"] = { arg:["campaign","","1"] };

te["schedule_campaign_tag_txa"] = { };

te["schedule_voiceprompt_tag_txa"] = { };

te["schedule_user_tag_txa"] = { };

te["schedule_ed_sub_user"] = { c: 
[

	{ div:["t15"], c: // user_id
	[
		{ s:["c w13 x y07 cb","User"] },
		{ div:["c"], enum_ls:["tag-r_--o-schedule_user_tag_txa-%1-user_id-%0-", "user_ls-users", 
"c w10 x b02", 
"schedule_user_tag_txa","r_", 
":v:schedules:user_id", "schedule_user_tag_txa", ":v:schedules:user_usn", "user_id", " %0", "", "0", "noop", 
"dd w28 x y mtn1 gw ba", 
"noop"] },
		{ div:["e"] }
	]},

	{ arg:["","campaign_id","0"] },

	{ div:["t15"], c: // workinghours, reattempt
	[
		{ s:["c w13 x y07 cb","Action"] },
		{ div:["c"], enum_sel:["tag-r_--o--:0::priority:1-priority-%0-%0",
"c w15 x b02", 
":v:priority:priority", "",":v:priority:priority::priority:1","priority"," %0"," %0", 
"dd w13 x y mtn1 gw ba", "schedule_ed_priority_r","priority_user",
"noop"] },
		{ div:["e"] }
	]},
]};

te["schedule_ed_campaign"] = { c:
[
	{ div:["t15"], c:
	[
		{ s:["c w13 x y07 cb","Campaign"] },
		{ div:["c"], enum_ls:["tag-r_--o-schedule_campaign_tag_txa-%1-campaign_id-%0-", "campaign_ls-campaigns", 
"c w25 x b02", 
"schedule_campaign_tag_txa","r_", 
":v:schedules:voiceprompt_id", "schedule_campaign_tag_txa", ":v:schedules:voiceprompt_name", "voiceprompt_id", " %0", "", "0", null, 
"dd w28 x y mtn1 gw ba", 
"noop"] },
		{ div:["e"] }
	]},

	{ div:["t15"], c:
	[
		{ s:["c w13 x y07 cb","IVR Menu"] },
		{ div:["c"], enum_ls:["tag-r_--o-schedule_voiceprompt_tag_txa-%1-voiceprompt_id-%0-", "voiceprompt_ls-voiceprompts", 
"c w25 x b02", 
"schedule_voiceprompt_tag_txa","r_", 
":v:schedules:voiceprompt_id", "schedule_voiceprompt_tag_txa", ":v:schedules:voiceprompt_name", "voiceprompt_id", " %0", "", "0", "noop", 
"dd w28 x y mtn1 gw ba", 
"noop"] },
		{ div:["e"] }
	]},

	{ div:["t15"], c: 
	[
		{ s:["c w13 x y07 cb","Action"] },
		{ div:["c"], enum_sel:["tag-r_--o--:0::priority:1-priority-%0-%0",
"c w15 x b02", 
":v:priority:priority", "",":v:priority:priority::priority:1","priority"," %0"," %0", 
"dd w13 x y mtn1 gw ba", "schedule_ed_priority_r",null,
"noop"] },
		{ div:["e"] }
	]}
]};

te["schedule_ed_sub_voiceblast"] = { schedule_ed_campaign:["campaign_arg_voiceblast","priority_outbound"] };
te["schedule_ed_sub_outbound"] = { schedule_ed_campaign:["campaign_arg_outbound","priority_outbound"] };
te["schedule_ed_sub_inbound"] = { schedule_ed_campaign:["campaign_arg_inbound","priority_inbound"] };

// -----------

te["schedule_ed_type_sel_sub"] = { div:["","sub"], c:
[
        { arg:["schedule_ed_sub_inbound,schedule_ed_sub_outbound,schedule_ed_sub_voiceblast,schedule_ed_sub_user-r_-ve-_type_","","1,2,3,4"] },
]};

te["schedule_ed_priority_r"] = { div:[], ac:["ay","","_sel","xx tt b05 cb",""], c: // 
[
        { s:["","%1"] },
        { div:["e"], c:[ { arg:["-0","","%0"] }, { arg:["-2","","%0"] } ] }
]};

te["schedule_ed_type_r"] = { div:[], ac:["ay","","_sel","xx tt b05 cb",""], c: // 
[
        { s:["","%1"] },
        { div:["e"], c:[ { arg:["-0","","%0"] }, { arg:["-2","","%0"] } ] }
]};

te["schedule_ed_dayofweek_r"] = { div:["x"], c:
[
        { input:["g","dayofweek","","%0","checkbox","%9"] },
        { ac:["r ay","","_chk","h02 x y cb",""], c:
        [ 
                { div:["c w01_ t"], s:["chk",""] },
                { div:["c"], s:["x t h02","%2"] },
                { div:["e"] }
        ]}
]};

te["schedule_ed_r_"] = { div:["","ve"], c:
[
	{ div:["t15"], c:
	[
		{ s:["c w13 x y07 cb","Date Range"] },
	 	{ div:["c"], c:
                [
                        { div:["","calw"], c:
                        [
                                { li:["w32 ay cb ba","va"], c:[ { div:[""], ev:["_dd"], c:
                                [
                                        { p:["c w26 l b05","o"], c:[ { p:["","calv"], ucalv:[" :0:d:dmy: ","daterange",":v:schedules:daterange"] } ] }, 
					{ div:["d w02 x y"],  c:[ { div:["h02 w02 awb"] } ] },
                                        //{ div:["d w02 x t content-hidden_"],  c:[ { div:["h01_ w02 awb"] } ] },
                                        //{ div:["d w02 x t content-shown_"],  c:[ { div:["h01_ w02 awt"] } ] },
                                        { div:["e"] }
                                ]} ]},
                                { div:["dd w40_ xx b10 ba mtn1 gw","vdd"], ev:["_undd"], c:
                                [ 
                                        { div:[], c:
                                        [
                                                { ucal:["daterange","","noop","2","Start Date", "End Date"] },
                                                { div:["e"] },
                                                { div:["c x"], aci:["ay","_vcal0","_cal_vw","x y tc ba_w cbl","l0","Day"] },
                                                { div:["c x"], aci:["ay","_vcal1","_cal_vw","x y tc ba_w cbl","l1","Range"] },
                                                { div:["e"] }
                                        ]}
                                ]}
                        ]}
                ]},
		{ div:["e"] }
	]},

	{ div:["t15"], c:
	[
		{ s:["c w13 x y07 cb","Start Time"] },
		{ div:["c"], c:
                [
                        { li:["w14 ba","va"], c:[ { div:[], ev:["_dd"], c:
                        [
                                  { p:["c w10 l b05","o"], c:[ { p:["","timev"], uchk:["tag_time",":v:schedules:tm0","","", ":v:schedules:tm0:p::","tm0"," %0"] } ] }, 
				{ div:["d w02 x y"],  c:[ { div:["h02 w02 awb"] } ] },
				{ div:["e"] }
                        ]} ]},
                        { div:["dd w30 l y ba  gw cb","vdd"], ev:["_undd"], c:
                        [
                                { utime:["tm0",":v:schedules:tm0"] }
                        ]}
                ]},
		{ div:["e"] }
	]},

	{ div:["t15"], c:
	[
		{ s:["c w13 x y07 cb","End Time"] },
                { div:["c"], c:
                [
                        { li:["w14 ba","va"], c:[ { div:[], ev:["_dd"], c:
                        [
                                { p:["c w10 l b05","o"], c:[ { p:["","timev"], uchk:["tag_time",":v:schedules:tm1","","", ":v:schedules:tm1:p::","tm1"," %0"] } ] }, 
				{ div:["d w02 x y"],  c:[ { div:["h02 w02 awb"] } ] },
				{ div:["e"] }
                        ]} ]},
                        { div:["dd w30 l y ba  gw cb","vdd"], ev:["_undd"], c:
                        [
                                { utime:["tm1",":v:schedules:tm1"] }
                        ]}
                ]},
		{ div:["e"] }
	]},

	{ div:["t15"], c:
	[
		{ s:["c w13 x y07 cb","Day of Week"] },
		{ div:["c","taga-r_--o--:0::dayofweek:1-dayofweek-%0-"], c:
                [
                        { li:["w32 ba","va"], c:[ { div:["",""], ev:["_dd"], c:
                        [
                                { p:["c w28 l b05","o"], uchk:["taga",":v:schedules:dayofweek","","", ""," :0::dayofweek:1","dayofweek"," %0",""] }, 
				{ div:["d w02 x y"],  c:[ { div:["h02 w02 awb"] } ] },
                                { div:["e"] }
                        ]} ]},
                        { div:["dd w32 mtn1 y ba gw cb","vdd"], ev:["_undd"], c:
                        [
                                { uchk:["schedule_ed_dayofweek_r",":v:schedules:dayofweek","dayofweek"] }
                        ]}
                ]},
		{ div:["e"] }
	]},

	{ div:["t15"], c:
	[
		{ s:["c w13 x y07 cb","Resource Type"] },
		{ div:["c"], enum_sel:["tag-r_--o--:0::resource:1-resource-%0-%0",
"c w10 x b02", 
":v:schedules:resource", "",":v:schedules:resource::resource:1","resource"," %0"," %0", 
"dd w13 x y mtn1 gw ba", "schedule_ed_type_r","resource",
"schedule_ed_type_sel_sub"] },
		{ div:["e"] }
	]},

	{ p:["","_type_"], usub:["schedule_ed_sub_inbound,schedule_ed_sub_outbound,schedule_ed_sub_outbound,schedule_ed_sub_user","1,2,3,10",":v:schedules:resource"] },

	{ div:["t30 x"], vp_sav:[null,"_postj","Save","Saving...",null,null] }		
]};

te["schedule_new_r"] = { schedule_ed_r_:["schedule_new-schedules","","_vpclose"] };

te["schedule_new"] = { vped:["w51 ma gw bd sh__","New Schedule","schedule_new_r"] };

// ------------------------------------------------------------------------------

te["schedule_footer"] = { div:["bt"], c:
[
	{ div:["d y07 s"], pg:["pgto","schedule_list-schedules"," dh","da dl","schedule_list-schedules"," dh","da dr"] },
	{ div:["e"] }
]};

te["schedule_r_outbound"] = { div:["x y"], c:
[
	{ s:["c x y h01_",":v:schedules:campaign_name"] },
	{ s:["c x y h01_",":v:schedules:voiceprompt_name"] },
	{ div:["e"] }
]}

te["schedule_r_inbound"] = { s:["xx yy h01_",":v:schedules:voiceprompt_name"] };

te["schedule_r_user"] = { s:["xx yy h01_",":v:schedules:user_usn"] };

te["schedule_r_"] = { c:
[
	{ li:["w160","schedule_vw_id-schedules-^"], ev:["_vp"], c:
	[
        	{ div:["c w10"], s:["xx yy h01_",":v:schedules:resource"] },
		{ div:["c w25"], usub:["schedule_r_inbound,schedule_r_outbound,schedule_r_outbound,schedule_r_user","1,2,3,10",":v:schedules:resource"] },
        	{ div:["c w10"], s:["xx yy h01_",":v:schedules:priority"] },
        	{ div:["c w25"], s:["xx yy h01_",":v:schedules:daterange"] },
		{ div:["c w25"], s:["xx yy h01_",":v:schedules:dayofweek"] },
        	{ div:["c w07"], s:["xx yy h01_",":v:schedules:timerange"] },
        	{ div:["c w07"], s:["xx yy h01_",":v:schedules:end_ts"] },
        	{ div:["c w15"], s:["xx yy h01_",":v:schedules:created_by"] },
		{ div:["c w15"], s:["xx yy h01_",":1:d:dmyhnr: :0"] },
        	{ div:["e"], arg:["",".id",":v:schedules:id"] }
	]},
	{ div:["","schedule_r_-schedules-va"], c:[ { arg:["",".id",":v:schedules:id"] } ] }
]};

te["schedule_r"] = { div:["","va"], schedule_r_:[] };

te["schedule_k"] = { div:["gww"], s:["w160 gww",""], c: // activate filter ctx
[
	{ k_a:["c w20","","cd","Date Range","da db",    "daterange",":k:schedules_k:daterange:2"] },
	{ k_a:["c w20","","cd","Time Range","da db",	"timerange",":k:schedules_k:timerange:2"] },
	{ k_a:["c w25","","cd","Day of Week","da db",   "dayofweek",":k:schedules_k:dayofweek:2"] },
	{ k_a:["c w25","","cd","Resource Name","da db", "",""] },
	{ k_a:["c w15","","cd","Type","da db",		"res",":k:schedules_k:res:2"] },
	{ k_a:["c w15","","cd","Priority","da db",	"priority",":k:schedules_k:priority:2"] },
	{ k_a:["c w15","","cd","Created By","da db",   	"created_by_id",":k:schedules_k:created_by_id:2"] },	
	{ k_a:["c w15","","cd","Created On","da db",   	"created_on",":k:schedules_k:created_on:2"] },
	{ div:["e"], c:
	[ 
		{ arg:["","user_id",":k:schedules_k:user_id:2"] }, 
		{ arg:["","voiceprompt_id",":k:schedules_k:voiceprompt_id:2"] }, 
		{ arg:["","campaign_id",":k:schedules_k:campaign_id:2"] },
	]}
]};

te["schedule_nb"] = { div:[], c:[ { u:["nb","schedules_nb"] }, { div:["e"] } ] };

te["schedule_title"] = { div:[] }; 

te["schedule_list"] = { list:["schedule_title","schedule_nb","bl br bt ox","schedule_k","schedule_r","schedules","schedule_footer"] },

te["schedules"] = { c:
[
	{ div:["x15 t15 sshb","vb"], c:
	[
		{ div:["c x"], c:
		[
			{ div:["y","va"], s:["",""], c:
			[
				// { input:["g","","schedule_t_","0","radio","1"] },
				{ ac:["c ","schedule_main-schedules-vftab","_u","x y cb b h3",""], c:[ { s:["","Schedules"] } ] },
				{ div:["e"] }
			]},
		]},
		{ div:["c l20 y"], c:
		[
			{ ac:["aa","schedule_f-schedules_f","_vpf","x cd bd",""], c:
			[ 
				{ s:["c t04 micon h3","filter_alt"] }, 
				{ div:["c x y s","","Filter"] }, 
				{ div:["e"] }
			]}
		]},
		{ div:["c l20 y"], c:
		[
			{ ac:["aa","schedule_new-r_-^","_vp","xx cd bd",""], c:
			[ 
				{ s:["c t03 b h2","+"] }, 
				{ div:["c l y s","","New"] }, 
				{ div:["e"] }
			]},
			{ div:["","schedule_main-schedules-vftab"] }
		]},
		{ div:["e"], c:[ { arg:["","","schedule_list-schedules"] }, { arg:["","","0"] }, { arg:["","","0"] }, { arg:["","",""] } ] }
	]},
	{ div:["x25 t","vf"], c:
	[ 
		{ div:[] },
		{ li:["","schedule_f-schedules_f"], ev:["__vpf"] }
	]},
	{ div:[], c:
	[
		{ div:[], c:[ { input:["g","","schedule_v","0","radio","1"] }, { p:["tabv x20 yy","vt"], schedule_list:[] } ] },
		{ div:[], c:[ { input:["g","","schedule_v","1","radio"] }, { p:["tabv x20 yy","vt"] } ] },				
	]}
]};
