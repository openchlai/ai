// ----------------------------------------------

te["case_history_footer"] = { div:["bt_ y"], c:
[
	{ div:["d t03"], c:[ { ac:["nav","case_history-caseupdates","_nav","dh",""], c:[ { div:["da dr_"] }, { arg:["","_a","%0"] } ] }, { s:["navl","..."] } ] },
	{ div:["d t03"], c:[ { aci:["nav","case_history-caseupdates","_nav","dh","prev",""], c:[ { div:["da dl_"] }, { arg:["","_a","%0"] } ] }, { s:["navl","..."] } ] },
	{ s:["d x y cd s","%4"] },
	{ s:["d y cd s","of"] }, 
	{ s:["d x y cd s","%3"] },
	{ s:["d y cd s","-"] },
	{ s:["d x y cd s","%2"] },
	{ div:["e"] }
]};

te["case_history_r"] = { div:["bt_"], c:  // case_new, case_update, case_edit, case_type_update, reporter_edit, client_add, client_edit, perp_add, perp_edit
[
	{ s:["c w14 x y",":d:dmyhnr:1: "] },
	{ s:["c w08 x y","%2"] },
	{ ac:["ay","caseupdate_vw_id-caseupdates","____vp","y cb",""], c:
	[
		
		{ s:["c x t w10",":v:caseupdates:priority::case_priority:2"] },
		{ div:["c x t  w16"], c:
		[
			{ span:["","",":v:caseupdates:status::case_status:1"] },
			{ span:["x","",":v:caseupdates:escalatedto"] } 
		]},
		{ s:["c x t w50",":v:caseupdates:plan"] },
		{ div:["d w15"], c:
		[


		]},
		{ div:["e"], arg:["",".id","%0"] },
	]}
]};


te["case_history_k"] = { div:["g"], c:
[
	//{ arg:["","case_id",":v:caseupdates_k:case_id:2"] } // other filters
	{ k_a:["g","case_rr-cases","cd st","Case ID","da db","case_id",":k:caseupdates_k:case_id:2"] },
]};

te["case_history_title"] = { div:["y"], c:
[
	{ s:["x y b h3","Case History"] }

]};

te["case_history"] = { list:["case_history_title","end","","case_history_k","case_history_r","caseupdates","case_history_footer"] };
