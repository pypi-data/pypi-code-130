import ruamel.yaml

neccessary_headings = {
	"general options" : {
			"start": None,
			"end" : None,
			"instruments": "H1L1V1",
			"min-instruments": 1,
			},
	"data product options" : {
			"data" : {
				"template-bank" : {},
				},
			},
	"data source options" : {
			"source" : {
				"data-source" : "frames",
				"frame-type" : {},
				"channel-name" : {},
				"sample-rate" : 4096,
				"frame-segments-file" : "segments.xml.gz",
				"frame-segments-name" : "datasegments",
				},
			},
	"segments options" : {
			"segments" : {
				"backend" : "dqsegdb",
				"science" : {},
				"vetoes" : {
					"category" : CAT1,
					"veto-definer" : {
						"file" : None,
						"version" : None,
						"epoch" : None,
						},
					},
				},
			},
	"psd options" : {
			"psd" : {
				"fft-length" : 32,
				"sample-rate" : 4096,
				},
			},
	"svd bank options" : {
			"svd" : {
				"approximant" : ["0:1.73:TaylorF2", "1.73:1000:SEOBNRv4_ROM"],
				"tolerance" : 0.9999,
				"max-f-final" : 1024.0,
				"sample-max-64" : 2048,
				"sample-max-256" : 2048,
				"autocorrelation-length" : ["0:15:701", "15:1000:351"],
				"sub-banks" : {
						"bank1" : {
							"f-low" : 15.0,
							"overlap" : 50,
							"sort-by": "mchirp",
							"num-banks" : 3,
							"num-split-templates" : 334,
							"num-chi-bins" : 20,
							"samples-min" : 2048,
							},
						},
				"manifest" : "H1L1V1-GSTLAL_SVD_MANIFEST-0-0.json",
				},
			},
	"filtering options" : {
			"filter" : {
				"fir-stride" : 1,
				"coincidence-threshold" : 0.005,
				"min-instruments" : 1,
				"veto-segments-file" : "vetoes.xml.gz",
				"ht-gate-threshold" : "0.8:15.0-45.0:100.0",
				"time-slide-file" : "tisi.xml",
				"injection-time-slide-file" : "inj_tisi.xml",
				"time-slides" : {
						"H1": "0:0:0",
						"L1": "0.62831:0.62831:0.62831", 
						"V1": "0.31415:0.31415:0.31415",
						},
				"injections" : {
					"all" : {
						"file" : "combined_injections.xml",
						"range" : "0.01:1000.0",
						},
				},
			},
			},
	"injection options" : {
			"injections" : {
				"combine" : True,
				"combined-file" : "combined_injections.xml",
				"expected-snr" : {
						"f-low" : 15.0,
						},
				"sets" : {
						"bns-broad" : {
							"f-low" : 14.0,
							"seed" : 38439,
							"time" : {
								"step" : 32,
								"interval": 1,
								"shift" : 8,
								},
							"waveform": "SpinTaylorT4threePointFivePN",
							"mass-distr": "componentMass",
							"mass1" : {
								"min" : 1.0,
								"max" : 3.0,
								},
							"mass2" : {
								"min" : 1.0,
								"max" : 3.0,
								},
							"spin1" : {
								"min" : 0.00,
								"max" : 0.05,
								},
							"spin2" : {
								"min" : 0.00,
								"max" : 0.05,
								},
							"distance" : {
								"min" : 10000,
								"max" : 400000,
								},
							"file" : "bns_broad_injections.xml",
							},
					},
				},
			},
	"prior options" : {
			"mass-model" : "mass_model/o3_bank_logmass_mass_model.h5",
			"dtdphi" : {
				"nsbh" : "inspiral_dtdphi_pdf/fixed_background/inspiral_dtdphi_pdf.h5",
				"bbh_1" : "inspiral_dtdphi_pdf/fixed_background/inspiral_dtdphi_pdf.h5",
				"bbh_2" : "inspiral_dtdphi_pdf/fixed_background/inspiral_dtdphi_pdf.h5", 
				"imbh" : "inspiral_dtdphi_pdf/inspiral_dtdphi_pdf.h5",
				},
			},
	"ranking options" : {
			"rank" : {
				"ranking-stat-samples" : 4194304,
				},
			},
	"summary options" : {
			"summary" : {
				"webdir" : None,
				},
			},
	"condor options" : {
			"condor" : {
				"profile" : "ldas",
				"accounting-group" : "ligo.dev.o3.cbc.uber.gstlaloffline",
				"singularity-image" : None,
				"transfer-files" : False,
				},
			},
	}
	
def write_section(yaml_file, section_heading, yaml_dict):
	yaml_file.write("##--------------------------------\n"
	yaml_file.write("# " + section_heading + "\n\n")
	ruamel.yaml.dump(yaml_dict, yaml_file)



	
	
