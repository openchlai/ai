

te["qa_score_yes_no"] = { p:["x y","o"], c:[ { li:[], c:
[
	{ s:["c y w02",null] },
	{ s:["c y w50 n",null] }, 

	{ input:["g","score",null,"0","radio"] },
	{ ac:["d ba mln1 opti","","_qa_opt","xx y cb ","No"] }, 
		
	{ input:["g","score",null,"1","radio"] },
	{ ac:["d ba mln1 opti","","_qa_opt","xx y cb ","Partialy"] }, 
		
	{ input:["g","score",null,"2","radio"] },
	{ ac:["d ba mln1 opti","","_qa_opt","xx y cb ","Yes"] }, 
			
	{ div:["e"] },
]} ]};

te["qa_ed_comment"] = { p:["x y","o"], c:
[
	{ s:["c y w02",null] },
	{ s:["c y n",null] },
	{ div:["e"] },
	{ ta:["ml2 ba","w67 h10 x y","",null,""] }
]};

te["qa_ed_section_title"] = { s:["x07 t15 b10 b cb n",null] };

te["qa_tabi"] = { div:[null], c: 	// 
[
	{ input:["g","",null,null,"radio",null] },
	{ li:["cb gws_ tabi_",null], ev:[null], c:
	[
		{ div:["xx t h04"], c:
		[
			{ s:["d n",null] },
			{ s:["c w07",null] },
			{ div:["e"] }
		]},
		{ div:["y"], c:
		[
			{ s:["d x",null] },
			{ s:["d h",null] },
			{ div:["e"] }
		]}
	]},
]};

te["qa_nav"] = { div:["x yy"], c:
[
	{ ac:["c w08","prev","_qa_nav","x y04 gws_ bd_ cb n tc",""], c:[ { s:["","Previous"] }, { arg:["","",null] } ] },
	{ ac:["d w08","","_qa_nav","x y04 gws_ bd_ cb n tc",""], c:[ { s:["","Next"] }, { arg:["","",null] } ] },
	{ div:["e"] }
]};
		
te["qa_ed_r"] = { div:["","ve"], c: // 
[
	{ div:["yy r05","vb"], c:
	[
		{ qa_tabi:["c w11 mr", "qaed","0","1", "","_tab", "0","Opening / Greeting"," %","0"] },
		{ qa_tabi:["c w11 mr", "qaed","1","", "","_tab", "0","Listening"," %","0"] },
		{ qa_tabi:["c w11 mr", "qaed","2","", "","_tab", "0","Pro-activeness"," %","0"] },
		{ qa_tabi:["c w11 mr", "qaed","3","", "","_tab", "0","Resolution / Counselling"," %","0"] },
		{ qa_tabi:["c w11 mr", "qaed","4","", "","_tab", "0","Hold Procedures"," %","0"] },
		{ qa_tabi:["c w11 mr", "qaed","5","", "","_tab", "0","Closing"," %","0"] },
		{ qa_tabi:["c w11 mr", "qaed","6","", "","_tab", "","Feedback","","&nbsp;"] },		
		{ div:["d w12 ba"], c:
		[
			{ div:["xx t h04 h b"], c:
			[
				{ s:["d n"," 0"] },
				{ s:["c n","Total Score"] },
				{ div:["e"] }
			]},
			{ div:["y b"], c:
			[
				{ s:["d x"," %"] },
				{ s:["d h"," 0"] },
				{ div:["e"] }
			]}
		]},
		
		{ div:["e"] }
	]},
	
	{ div:["x"], c:[ { p:["c","nb"] }, { div:["e"] } ] },
	
	{ div:["w70 tt"], c:
	[
		{ div:[], c:
		[
			{ input:["g","","qtv","0","radio","1"] },
			{ div:["tabv"], c:
			[
				{ div:["h40"], c:
				[
					{ qa_ed_section_title:["Opening Call Greeting"] },
					{ qa_score_yes_no:["1.","Use of call opening phrase",  "opening_phrase","opening_phrase","opening_phrase"]  }, 
					{ qa_ed_comment:["2.","Section Comments","opening_phrase_comments"] },
				]},
				{ div:["x yy"], c:
				[
					{ ac:["d w08","","_qa_nav","x y gws_ bd_ cb n tc",""], c:[ { s:["","Next"] }, { arg:["","","1"] } ] },
					{ div:["e"] }
				]}
			]},
		]},
	
		{ div:[], c:
		[
			{ input:["g","","qtv","1","radio"] },
			{ div:["tabv"], c:
			[
				{ div:["h40"], c:
				[
					{ qa_ed_section_title:["Listening Skills"] },
					{ qa_score_yes_no:["1.","Caller was not interrupted during the conversation", "non_interrupting","non_interrupting","non_interrupting"]  }, 
					{ qa_score_yes_no:["2.","Empathizes with the caller on the issues raised",   "empathy","empathy","empathy"]  }, 
					{ qa_score_yes_no:["3.","Rephrases or paraphrases the issues / query back to caller.",   "paraphrasing","paraphrasing","paraphrasing"]  },
					{ qa_score_yes_no:["4.","Uses 'please' and 'thank you' when requesting and receiving information.",   "courteous", "courteous","courteous"]  },
					{ qa_score_yes_no:["5.","Does not hesitate or sound unsure when providing feedback.",   "nonhesitant", "nonhesitant","nonhesitant"]  },
					{ qa_ed_comment:["6.","Section Comments","listening_comments"] },
				]},
				{ qa_nav:["0","2"] }
			]}
		]},
		
		{ div:[], c:
		[
			{ input:["g","","qtv","2","radio"] },
			{ div:["tabv"], c:
			[
				{ div:["h40"], c:
				[
					{ qa_ed_section_title:["Pro-activeness"] },
					{ qa_score_yes_no:["1.","Willingness to solve additional issues not proposed by the client.", "extra_mile_willingness","extra_mile_willingness","extra_mile_willingness"]  }, 
					{ qa_score_yes_no:["2.","Confirmation of client's satisfaction with action points given",   "confirms_client_satisfaction","confirms_client_satisfaction","confirms_client_satisfaction"]  }, 
					{ qa_score_yes_no:["3.","Follows up on case updates.",   "follows_up_on_case_updates","follows_up_on_case_updates","follows_up_on_case_updates"]  },
					{ qa_ed_comment:["4.","Section Comments","pro_active_comments"] },
				]},
				{ qa_nav:["1","3"] }
			]}
		]},
		
		{ div:[], c:
		[
			{ input:["g","","qtv","3","radio"] },
			{ div:["tabv"], c:
			[
				{ div:["h40"], c:
				[
					{ qa_ed_section_title:["Resolution / Counselling provided"] },
					{ qa_score_yes_no:["1.","Gives accurate and precise information to the caller.", "accuracy","accuracy","accuracy"]  }, 
					{ qa_score_yes_no:["2.","Correct use of language. Wordings, phrases, greetings etc.",   "grammar","grammar","grammar"]  }, 
					{ qa_score_yes_no:["3.","If not sure of the information, did the counsellor consult.",   "consults","consults","consults"]  },
					{ qa_score_yes_no:["4.","Follows accurate steps while addressing the client's problem.",   "procedure_adherance", "procedure_adherance","procedure_adherance"]  },
					{ qa_score_yes_no:["5.","Explains in detail to the caller the process of doing the problem solving.",   "educative", "educative","educative"]  },
					{ qa_ed_comment:["6","Section Comments","resolution_comments"] },
				]},
				{ qa_nav:["2","4"] }
			]}
		]},
		
		{ div:[], c:
		[
			{ input:["g","","qtv","4","radio"] },
			{ div:["tabv"], c:
			[
				{ div:["h40"], c:
				[
					{ qa_ed_section_title:["Hold procedures"] },
					{ qa_score_yes_no:["1.","Provides an explanation/instructions to the caller before placing on hold/transfer and obtains consent", "notifies_hold","notifies_hold","notifies_hold"]  }, 
					{ qa_score_yes_no:["2.","Revisits caller, providing status and offering. Always thanks the caller for holding.",   "updates_hold","updates_hold","updates_hold"]  }, 
					{ qa_ed_comment:["3.","Section Comments","hold_comments"] },
				]},
				{ qa_nav:["3","5"] }
			]}
		]},
		
		{ div:[], c:
		[
			{ input:["g","","qtv","5","radio"] },
			{ div:["tabv"], c:
			[
				{ div:["h40"], c:
				[
					{ qa_ed_section_title:["Closing the Call"] },
					{ qa_score_yes_no:["1.","Demonstrates appreciation and thanks caller for calling", "call_closing_coutesy","call_closing_coutesy","call_closing_coutesy"]  }, 
					{ qa_ed_comment:["2.","Section Comments","call_closing_comments"] },
				]},
				{ qa_nav:["4","6"] }
			]}
		]},
		
		{ div:[], c:
		[
			{ input:["g","","qtv","6","radio"] },
			{ div:["tabv"], c:
			[
				{ div:["h40"], c:
				[
					{ qa_ed_section_title:["Feedback"] },
					{ qa_ed_comment:["","","feedback"] },
				]},
				{ div:["x yy"], c:
				[
					{ ac:["c w08","","_qa_nav","x y gws bd_ cb n tc",""], c:[ { s:["","Previous"] }, { arg:["","","5"] } ] },
					// { ac:["d w08 ag","","_postj","x y gb bd_ cw n tc","Finish"] },
					{ div:["d w08"], c:
					[
						{ ac:["btn ag","qa_form-qas","_postj","x y gb bd_ cw n tc","Finish"] }, 
						{ div:["savl"], s:["x y go bd_ cw n tc","Saving..."] }
					]},
					{ p:["e","o"], arg:["","chan_uniqueid","%5"] }
				]}
			]}
		]}
	]}
]};

te["qa_form"] = { div:["w100 ma bd sh__ gw_"], ev:["_undd"], c:
[
	{ div:["x15 tt"], c:
	[
		{ s:["c xx y12 n b","QA Form"] },
		{ ac:["d","","_uvp","xx y08 h cb","&Cross;"] },
		{ div:["e"] }
	]},
	{ div:["","va"], c:
	[
		{ div:["x25 x15 tt n"], c:
		[
			{ s:["c y b",":v:qas:chan_vector::vector:1"] }, 
			{ s:["c x y b","Call"] },
			{ s:["c y b",":v:qas:chan_vector::vector:3"] },
			{ s:["c x y b",":v:qas:chan_phone"] },
			{ s:["c y b",":v:qas:chan_vector::vector:6"] },
			{ s:["c x y b",":v:qas:chan_usr"] },		
			{ s:["c xx y cd",":d:dmyhn:6: "] },
			{ div:["d"], ac:["ao ","vfile_vw_r-calls-va-play","_u","y03 gws cb",""], c:
			[ 
				{ s:["c x h3_ micon","play_arrow"] },
				{ s:["c y02","Talk Time"] },
				{ s:["c xx y02",":h:ms:11:"] },	
				{ div:["e"], c:[ { arg:["",".id",":v:qas:chan_uniqueid"] }, { arg:["","file","wav"] } ] },
			]},
			{ div:["e"]}
		]},
		{ div:["x25"], c:
		[
			{ p:["d t02","play"] },
			{ div:["e"] }
		]},
	]},
	{ div:["x20 tt","ve"], qa_ed_r:[] },
]};

// ------------------------------------------------------------------------

rk["qa_yes_no"] = ["0","1","2"];
re["qa_yes_no"] = 
{
"0":["0","No"],
"1":["1","Partialy"],
"2":["2","Yes"],
};

te["qa_vw_yes_no_r"] = { div:["d"], c:
[
	{ input:["g","score","v","1","radio","%9"] },
	{ li:["d ba_w mln1 opti xx y cb ","","%1"] }
]};

te["qa_vw_yes_no"] =  { form:[], c:[ { li:[], c:
[
	{ s:["c y w02",null] },
	{ s:["c y w50 n",null] }, 
	{ uchk:["qa_vw_yes_no_r",null,"qa_yes_no"] },
	{ div:["e"] }
]} ]};

te["qa_vw_comment"] = { div:["x y","o"], c:
[
	{ s:["c y w02",null] },
	{ s:["c y n",null] },
	{ div:["e"] },
	{ div:["ml2"], s:["w67 h10 x y",null] }
]};

te["qa_vw_id"] = { div:["w100 ma bd sh__ gw","vddvw"], ev:["_undd"], c:
[
	{ div:["x15 tt"], c:
	[
		{ s:["c xx y12 n b","QA Results"] },
		{ ac:["d","","_uvp","xx y08 h cb","&Cross;"] },
		{ div:["e"] }
	]},
	{ div:["","va"], c:
	[
		{ div:["x25 x15 tt n"], c:
		[
			{ s:["c y b",":v:qas:chan_vector::vector:1"] }, 
			{ s:["c x y b","Call"] },
			{ s:["c y b",":v:qas:chan_vector::vector:3"] },
			{ s:["c x y b",":v:qas:chan_phone"] },
			{ s:["c y b",":v:qas:chan_vector::vector:6"] },
			{ s:["c x y b",":v:qas:chan_usr"] },		
			{ s:["c xx y cd",":d:dmyhn:6: "] },
			{ div:["d"], ac:["ao ","vfile_vw_r-calls-va-play","_u","y03 gws cb",""], c:
			[ 
				{ s:["c x h3_ micon","play_arrow"] },
				{ s:["c y02","Talk Time"] },
				{ s:["c xx y02",":h:ms:11:"] },	
				{ div:["e"], c:[ { arg:["",".id",":v:qas:chan_uniqueid"] }, { arg:["","file","wav"] } ] },
			]},
			{ div:["e"]}
		]},
		{ div:["x25"], c:
		[
			{ p:["d t02","play"] },
			{ div:["e"] }
		]},
	]},
	{ div:["x20 tt gw"], c:
	[
		{ div:["yy r05","vb"], c:
		[
			{ qa_tabi:["c w11 mr", "qaed","0","1", "","_tab", ":v:qas:greeting_score","Opening / Greeting"," %",":v:qas:greeting_score_p"] },
			{ qa_tabi:["c w11 mr", "qaed","1","", "","_tab", ":v:qas:listening_score","Listening"," %",":v:qas:listening_score_p"] },
			{ qa_tabi:["c w11 mr", "qaed","2","", "","_tab", ":v:qas:proactive_score","Pro-activeness"," %",":v:qas:proactive_score_p"] },
			{ qa_tabi:["c w11 mr", "qaed","3","", "","_tab", ":v:qas:resolution_score","Resolution / Counselling"," %",":v:qas:resolution_score_p"] },
			{ qa_tabi:["c w11 mr", "qaed","4","", "","_tab", ":v:qas:holding_score","Hold Procedures"," %",":v:qas:holding_score_p"] },
			{ qa_tabi:["c w11 mr", "qaed","5","", "","_tab", ":v:qas:closing_score","Closing"," %",":v:qas:closing_score_p"] },
			{ qa_tabi:["c w11 mr", "qaed","6","", "","_tab", "","Feedback","","&nbsp;"] },		
			{ div:["d w12 ba"], c:
			[
				{ div:["xx t h04 h b"], c:
				[
					{ s:["d n",":v:qas:total_score"] },
					{ s:["c n","Total Score"] },
					{ div:["e"] }
				]},
				{ div:["y b"], c:
				[
					{ s:["d x"," %"] },
					{ s:["d h",":v:qas:total_score_p"] },
					{ div:["e"] }
				]}
			]},
		
			{ div:["e"] }
		]},
	
		{ div:["x"], c:[ { p:["c","nb"], u:["nb","qas_nb"] }, { div:["e"] } ] },
	
		{ div:["w70 tt"], c:
		[
			{ div:[], c:
			[
				{ input:["g","","qtv","0","radio","1"] },
				{ div:["tabv"], c:
				[
					{ div:["h40"], c:
					[
						{ qa_ed_section_title:["Opening Call Greeting"] },
						{ qa_vw_yes_no:["1.","Use of call opening phrase",  ":v:qas:opening_phrase"]  }, 
						{ qa_vw_comment:["2.","Section Comments",":v:qas:opening_phrase_comments"] },
					]},
					
				]},
			]},
	
			{ div:[], c:
			[
				{ input:["g","","qtv","1","radio"] },
				{ div:["tabv"], c:
				[
					{ div:["h40"], c:
					[
						{ qa_ed_section_title:["Listening Skills"] },
						{ qa_vw_yes_no:["1.","Caller was not interrupted during the conversation", ":v:qas:non_interrupting"]  }, 
						{ qa_vw_yes_no:["2.","Empathizes with the caller on the issues raised",   ":v:qas:empathy"]  }, 
						{ qa_vw_yes_no:["3.","Rephrases or paraphrases the issues / query back to caller.",   ":v:qas:paraphrasing"]  },
						{ qa_vw_yes_no:["4.","Uses 'please' and 'thank you' when requesting and receiving information.",   ":v:qas:courteous"]  },
						{ qa_vw_yes_no:["5.","Does not hesitate or sound unsure when providing feedback.",   ":v:qas:nonhesitant"]  },
						{ qa_vw_comment:["6.","Section Comments",":v:qas:listening_comments"] },
					]},
				]}
			]},
			
			{ div:[], c:
			[
				{ input:["g","","qtv","2","radio"] },
				{ div:["tabv"], c:
				[
					{ div:["h40"], c:
					[
						{ qa_ed_section_title:["Pro-activeness"] },
						{ qa_vw_yes_no:["1.","Willingness to solve additional issues not proposed by the client.", ":v:qas:extra_mile_willingness"]  }, 
						{ qa_vw_yes_no:["2.","Confirmation of client's satisfaction with action points given",   ":v:qas:confirms_client_satisfaction"]  }, 
						{ qa_vw_yes_no:["3.","Follows up on case updates.",   ":v:qas:follows_up_on_case_updates"]  },
						{ qa_vw_comment:["4.","Section Comments",":v:qas:pro_active_comments"] },
					]},

				]}
			]},
		
			{ div:[], c:
			[
				{ input:["g","","qtv","3","radio"] },
				{ div:["tabv"], c:
				[
					{ div:["h40"], c:
					[
						{ qa_ed_section_title:["Resolution / Counselling provided"] },
						{ qa_vw_yes_no:["1.","Gives accurate and precise information to the caller.", ":v:qas:accuracy"]  }, 
						{ qa_vw_yes_no:["2.","Correct use of language. Wordings, phrases, greetings etc.",   ":v:qas:grammar"]  }, 
						{ qa_vw_yes_no:["3.","If not sure of the information, did the counsellor consult.",   ":v:qas:consults"]  },
						{ qa_vw_yes_no:["4.","Follows accurate steps while addressing the client's problem.",   ":v:qas:procedure_adherance"]  },
						{ qa_vw_yes_no:["5.","Explains in detail to the caller the process of doing the problem solving.",   ":v:qas:educative"]  },
						{ qa_vw_comment:["6","Section Comments",":v:qas:resolution_comments"] },
					]},

				]}
			]},
		
			{ div:[], c:
			[
				{ input:["g","","qtv","4","radio"] },
				{ div:["tabv"], c:
				[
					{ div:["h40"], c:
					[
						{ qa_ed_section_title:["Hold procedures"] },
						{ qa_vw_yes_no:["1.","Provides an explanation/instructions to the caller before placing on hold/transfer and obtains consent", ":v:qas:notifies_hold"]  }, 
						{ qa_vw_yes_no:["2.","Revisits caller, providing status and offering. Always thanks the caller for holding.",   ":v:qas:updates_hold"]  }, 
						{ qa_vw_comment:["3.","Section Comments",":v:qas:hold_comments"] },
					]},

				]}
			]},
		
			{ div:[], c:
			[
				{ input:["g","","qtv","5","radio"] },
				{ div:["tabv"], c:
				[
					{ div:["h40"], c:
					[
						{ qa_ed_section_title:["Closing the Call"] },
						{ qa_vw_yes_no:["1.","Demonstrates appreciation and thanks caller for calling", ":v:qas:call_closing_coutesy"]  }, 
						{ qa_vw_comment:["2.","Section Comments",":v:qas:call_closing_comments"] },
					]},

				]}
			]},
		
			{ div:[], c:
			[
				{ input:["g","","qtv","6","radio"] },
				{ div:["tabv"], c:
				[
					{ div:["h40"], c:
					[
						{ qa_ed_section_title:["Feedback"] },
						{ qa_vw_comment:["","",":v:qas:feedback"] },
					]},
					
				]}
			]}
		]}
	]}
]};

// ------------------------------------------------------------------------

te["qa_f_tags"] = { c: 
[
	{ f:["CallDate",":k:qas_f:chan_chan_ts",			" :d:dmy:0: "," chan_chan_ts"] },

	{ f:["Talk Time (in seconds)",":k:qas_f:chan_talk_time",			" %0"," chan_talk_time"] },
	{ f:["Opening Score",":k:qas_f:greeting_score_p",		" %0"," greeting_score_p"] },
	{ f:["Listening Score",":k:qas_f:listening_score_p",		" %0"," listening_score_p"] },
	{ f:["Proactive Score",":k:qas_f:proactive_score_p",		" %0"," proactive_score_p"] },
	{ f:["Resolution Score",":k:qas_f:resolution_score_p",		" %0"," resolution_score_p"] },
	{ f:["Holding Score",":k:qas_f:holding_score_p",		" %0"," holding_score_p"] },
	{ f:["Closing Score",":k:qas_f:closing_score_p",		" %0"," closing_score_p"] },
	{ f:["Total Score",":k:qas_f:total_score_p",			" %0"," total_score_p"] },
	
	{ f:["Created On",":k:qas_f:created_on",			" :d:dmy:0: "," created_on"] },
	
	{ div:["e"] }
]};

te["qa_f"] = { div:["w55 ma sh__ y gw_","vddvf"], ev:["_undd"], c:
[
	{ s:["x20 tt b","Search"] },
	{ div:["x15 tt b20"], c:
	[
		{ div:["xx yy"], kf_d:["Call Date"," :d:dmy:0: ","chan_chan_ts",":k:qas_f:chan_chan_ts","chan_chan_ts",":k:qas_f:chan_chan_ts"] },
		// todo: counselor list
		
		{ div:["xx yy"], kf_s:["Talk Time (in seconds)","chan_talk_time",":k:qas_f:chan_talk_time"] },
		{ div:["xx yy"], kf_s:["Opening Score","greeting_score_p",":k:qas_f:greeting_score_p"] },
		{ div:["xx yy"], kf_s:["Listening Score","listening_score_p",":k:qas_f:listening_score_p"] },
		{ div:["xx yy"], kf_s:["Proactive Score","proactive_score_p",":k:qas_f:proactive_score_p"] },
		{ div:["xx yy"], kf_s:["Resolution Score","resolution_score_p",":k:qas_f:resolution_score_p"] },
		{ div:["xx yy"], kf_s:["Holding Score","holding_score_p",":k:qas_f:holding_score_p"] },
		{ div:["xx yy"], kf_s:["Closing Score","closing_score_p",":k:qas_f:closing_score_p"] },
		{ div:["xx yy"], kf_s:["Total Score","total_score_p",":k:qas_f:total_score_p"] },
				
		// todo: supervisor list
		{ div:["xx yy"], kf_d:["Created On"," :d:dmy:0: ","created_on",":k:qas_f:created_on","created_on",":k:qas_f:created_on"] },
	]},
	{ vp_apply:["qa_f_tags-qas_f"] }
]};

// ------------------------------------------------------------------------

te["qa_footer"] = { div:["x ba"], c:
[
	{ div:["d y07"], pg:["pgto","qa_list-qas"," dh","da dl","qa_list-qas"," dh","da dr"] },
	{ div:["e"] }
]};

te["qa_r"] ={ div:[], c:
[
	{ ac:["ay w200","qa_vw_id-qas","_vp","cb gw",""], c:
	[
		{ div:["c w14"], s:["tt b05 h01_  xx",":d:dmyhn:6: "] },
		{ div:["c w14"], s:["tt b05 h01_  xx",":v:qas:chan_user_name"] },		
		{ div:["c w10"], s:["tt b05 h01_  xx",":h:ms:11: "] },
		
		{ div:["c w10"], s:["tt b05 h01_  xx",""], c:[ { span:["","",":v:qas:greeting_score_p"] }, { span:["",""," %"]} ] },		
		{ div:["c w10"], s:["tt b05 h01_  xx",""], c:[ { span:["","",":v:qas:listening_score_p"] }, { span:["",""," %"]} ] },	
		{ div:["c w10"], s:["tt b05 h01_  xx",""], c:[ { span:["","",":v:qas:proactive_score_p"] }, { span:["",""," %"]} ] },	
		{ div:["c w10"], s:["tt b05 h01_  xx",""], c:[ { span:["","",":v:qas:resolution_score_p"] }, { span:["",""," %"]} ] },	
		{ div:["c w10"], s:["tt b05 h01_  xx",""], c:[ { span:["","",":v:qas:holding_score_p"] }, { span:["",""," %"]} ] },	
		{ div:["c w10"], s:["tt b05 h01_  xx",""], c:[ { span:["","",":v:qas:closing_score_p"] }, { span:["",""," %"]} ] },	
		{ div:["c w10"], s:["tt b05 h01_  xx",""], c:[ { span:["","",":v:qas:total_score_p"] }, { span:["",""," %"]} ] },	
	
		{ div:["c w14"], s:["tt b05 h01_  xx",":v:qas:created_by"] },	
		{ div:["c w14"], s:["tt b05 h01_  xx",":d:dmyhn:1: "] },
		{ div:["e"], arg:["",".id","%0"] }
	]},
	{ div:[] }
]};

te["qa_k"] = { div:["w200 bt bb"], s:["",""], c: 
[
	{ k_a:["c w14","qa_rr-qas","cd","Call Date","da db","chan_chan_ts",":k:qas_k:chan_chan_ts:2"] },
	{ k_a:["c w14","qa_rr-qas","cd","User","da db","chan_user_name",":k:qas_k:chan_user_name:2"] },
	{ k_a:["c w10","qa_rr-qas","cd","Talk Time","da db","chan_talk_time",":k:qas_k:chan_talk_time:2"] },
	
	{ k_a:["c w10","qa_rr-qas","cd st","Opening","da db","greeting_score_p",":k:qas_k:greeting_score_p:2"] },
	{ k_a:["c w10","qa_rr-qas","cd","Listening","da db","listening_score_p",":k:qas_k:listening_score_p:2"] },
	{ k_a:["c w10","qa_rr-qas","cd","Proactive","da db","proactive_score_p",":k:qas_k:proactive_score_p:2"] },
	{ k_a:["c w10","qa_rr-qas","cd","Resolution","da db","resolution_score_p",":k:qas_k:resolution_score_p:2"] },
	{ k_a:["c w10","qa_rr-qas","cd","Holding","da db","holding_score_p",":k:qas_k:holding_score_p:2"] },
	{ k_a:["c w10","qa_rr-qas","cd","Closing","da db","closing_score_p",":k:qas_k:closing_score_p:2"] },
	{ k_a:["c w10","qa_rr-qas","cd","Total Score","da db","total_score_p",":k:qas_k:total_score_p:2"] },
	
	{ k_a:["c w14","qa_rr-qas","cd","Supervisor","da db","created_by",":k:qas_k:created_by:2"] },
	{ k_a:["c w14","qa_rr-qas","cd st","Created On","da db","created_on",":k:qas_k:created_on:2"] },

	{ div:["e"] }
]};

te["qa_nb"] = { div:[], c:[ { u:["nb","qas_nb"] }, { div:["e"] } ] };

te["qa_title"] = { div:[] }; 

te["qa_list"] = { list:["qa_title","qa_nb","bl br ox","qa_k","qa_r","qas","qa_footer"] };

te["qa_main"] = { c:
[
	{ div:["tt","vb"], c:
	[
		{ div:["c t03"], c:
		[
			{ div:["","va"], s:["",""], c:
			[
				{ input:["g","","qa_t_","0","radio","1"] },
				{ ac:["c","qa_main-qas-vftab","_u","x y cb b h2","QA Results"] }, 
				//{ ac:["c t02 x ay","","_dd","h02 w02 gws_ awb",""] },
				{ div:["e"] } //, arg:["","_title","%5"] }
			]},
			{ div:["dd x y gw ba sh nd w14","vdd"], c:
			[
			
			]}
		]},
		
		{ div:["c l40"], c: 
		[
			{ arg:["qa_list-qas","","0"] },
			{ input:["g","","qas_t_","0","radio","1"] },
			{ li:["opto x bl bt bb gw s cb","qa_list-qas"], ev:["_tab"], c:
			[
				{ s:["c l t h3_ micon","list"] },
				{ div:["c xx y","","List"] }, 
				{ div:["e"] }
			]}
		]},

		{ div:["c"], c: 
		[
			{ arg:["qa_rpt_vw-qas-@","","1,0"] },
			{ input:["g","","qas_t_","1","radio"] },
			{ li:["opto x ba gw s cb","qa_rpt_main-r_"], ev:["_tab"], c:[ { div:[], c:
			[
				{ s:["c l t h3_ micon","bar_chart"] },
				{ s:["c xx y","Reports"] }, 
				{ div:["e"] }
			]} ]}
		]},

		{ div:["c l40"], ac:["ay","qa_f-qas_f","_vpf","x t01 bd_ cb s",""], c:
		[ 
			{ s:["c t04 h3_ micon","filter_alt"] },
			{ div:["c x y","","Filter"] }, 
			{ div:["e"] }
		]},

		{ div:["c l40"], ac:["ay","qas","_download","x t01 bd_ cb s",""], c:
		[ 
			{ s:["c t04 h3_ micon","download"] },
			{ div:["c x y","","Download"] }, 
			{ div:["e"] }
		]},
		
		{ div:["e"], c:[ { arg:["","","qa_list-qas"] }, { arg:["","","0"] }, { arg:["","","-1"] }, { arg:["","",""] } ] }
	]},

	{ div:["yy","vf"], c:[ { div:["","qa_f-qas_f"], c: // ev:["_n_vpf"], c:
	[
		{ qa_f_tags_k:[] }
	]} ]},

	{ div:[], c:
	[
		{ div:[], c:[ { input:["g","","qas_v","0","radio","1"] }, { p:["tabv yy","vt"], qa_list:[] } ] },
		{ div:[], c:[ { input:["g","","qas_v","1","radio"] }, { p:["tabv","vt"] } ] },				
	]}
]};
		
te["qas"] = { c:
[
	{ div:["g"], c:
	[
		
	]},
	{ form:[], c:
	[
		{ div:[], c:
		[	
			{ input:["g","","qas_mv","0","radio","1"] }, 
			{ p:["tabv x20 y20 gw mm","vftab"], qa_main:[] } 
		]},
		{ div:[], c:
		[	
			{ input:["g","","qas_mv","1","radio"] }, 
			{ p:["tabv gw yy mm","vfvw"] }
		]}
	]}
]};

function _qa_nav ()
{
	var p = __(this,"ve");
	var i = this.firstChild.childNodes[1].value;
	p.firstChild.childNodes[i].firstChild.checked=true;
	p.lastChild.childNodes[i].firstChild.checked=true;
}

function _qa_opt ()
{
	var g = [["opening_phrase"],
["non_interrupting","empathy","paraphrasing","courteous","nonhesitant"],
["extra_mile_willingness","confirms_client_satisfaction","follows_up_on_case_updates"],
["accuracy","grammar","consults","procedure_adherance","educative"],
["notifies_hold","updates_hold"],
["call_closing_coutesy"]];
	var gv = [2,10,6,10,4,2];
	var el = this.previousSibling;
	el.checked = true;
	var gtot = 0;
	var  p = __(this,"ve");
	var coll = p.firstChild.childNodes;
	var a = {}
	argv (p, a);
	// console.log (JSON.stringify (a))
	for (var i=0; i<6; i++)
	{
		var tot = 0;
		for (var j=0; j<g[i].length; j++)
		{
			// console.log (g[i][j]+" = "+ a[g[i][j]])
			if (a[g[i][j]]) tot+= (a[g[i][j]]*1)
		}
		gtot += tot;
		// console.log ("qa group: "+i+"="+tot+"  | "+gtot)
		coll[i].childNodes[1].childNodes[0].childNodes[0].innerHTML = ""+tot;
		coll[i].childNodes[1].childNodes[1].childNodes[1].innerHTML = ""+(Math.round (((tot/gv[i])*100),0));
	}
	
	coll[7].childNodes[0].childNodes[0].innerHTML = ""+gtot;
	coll[7].childNodes[1].childNodes[1].innerHTML = ""+(Math.round (((gtot/34)*100),0));
	
	
}

