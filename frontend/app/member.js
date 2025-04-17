
te["member_del"] = { div:["c g","va"], c:[ { arg:["o","member_id","%0"] }, { arg:["o","usergroup_id","0"] } ] };

te["member_ed"] = { div:["c","va"], s:["l ga bd cb mr mb",""], c:
[
	{ s:["c y04 cb","%8"] },
	{ arg:["o","user_id","%7"] },
	{ ac:["d l aa","member_del-members","_uchk","x y04 bd_ tc n cb","&Cross;"], c:
	[ 
		{ p:["","o"], c:
		[
			{ arg:[".id","","%0"] },
			{ arg:["campaign_id","","0"] },
		]},
	]},
	{ s:["d l20 y04 cb","::user_role:9:1"] }, 
	//{ s:["d x y04 w04 cb tr","%10"] },
	{ div:["e"] }
]};

te["member_add"] = { div:["c","va"], s:["l ga bd cb mr mb",""], c:
[
	{ s:["c y04 cb","%1"] },
	{ arg:["o","user_id","%0"] },
	{ ac:["d l aa","","_uchk","x y04 bd_ tc n cb","&Cross;"] },
	{ s:["d l20 y04 cb","::user_role:2:1"] }, 
	//{ s:["d x y04 w04 cb tr","%3"] },
	{ div:["e"] }
]};

// -------------------------------------------------------------------------------------------

te["member_tag_vw"] = { div:["w30 gws mb mr"], s:["",""], c:
[
	{ div:["c x t"], c:[ { img:["","","/voiceapps/images/user-black.png","15"] } ] },
	{ s:["c x y cb b","::user_role:9:1"] },
	{ s:["c y cb","%8"] }, 
	{ s:["d xx y tr","%10"] },
	{ div:["e"] }
]};

// ------------------------------------------------------------------------------------------

te["member_lst_footer"] = { div:["y07"], c:
[	
	{ div:["c","va"], ac:["aa","user_la-campaigns-vt","_u","x07 y03 gwd cb","Add / Remove"], c:[ { arg:["",".id",":k:members_k:campaign_id:2"] } ] }, 
	{ div:["d"], pg:["pgto","member_lst-members"," dh","da dl","member_lst-members"," dh","da dr"] },
	{ div:["e"] }
]};

te["member_lst_r"] = { li:["bt_"], c:
[
	{ div:["c w12"], c:
	[ 
		{ div:["c l t"], c:[ { img:["","","/voiceapps/images/user-black.png","13"] } ] },
		{ s:["c x y cb","::user_role:9:1"] },
		{ div:["e"] }
	]},
	{ div:["c w15"], s:["x y cb","%8"] }, 
	{ div:["c w15"], s:["x y cb","%10"] }, 
	{ div:["e"] }
]};

te["member_lst_rr"] = { c:
[
	{ u:["member_lst_r","members"] },
	{ p:["","whnew"] }
]}

te["member_lst_k"] = { c: 
[
	{ k_a:["c w12","","cd","Role","da db",	"priority",":k:members_k:priority:2"] },
	{ k_a:["c w15","","cd","Username","da db",	"daterange",":k:members_k:id:2"] },
	{ k_a:["c w15","","cd","Extension","da db",	"dayofweek",":k:members_k:id:2"] },
	//{ k_a:["d w15","","cd","Created On","da db",	"created_on",":k:members_k:created_on:2"] },
	{ arg:["","campaign_id",":k:members_k:campaign_id:2"] }
]};

te["member_lst_nb"] = { div:[], c:[ { u:["nb","members_nb"] }, { div:["e"] } ] };

te["member_lst_title"] = { div:["y","va"], c:
[
	{ div:["c","va"], ac:["","","","x y b cb","Assigned Agents"] }, 
	//{ div:["c l20 aa"], ac:["","call_f-calls_f","_vpf","x y cb b h3",""], c:[ { img:["","","/voiceapps/images/filter.png", "14"] } ] }, 
	{ div:["e"] }
]};

te["member_lst"] = { list:["member_lst_title","member_lst_nb","ba ov","member_lst_k","member_lst_rr","members_ctx", "member_lst_footer"] };

