#//////////////////////////////////////////////////////////////////////////////
#////                                                                       ///
#//// Copyright INRO, 2016-2017.                                            ///
#//// Rights to use and modify are granted to the                           ///
#//// San Diego Association of Governments and partner agencies.            ///
#//// This copyright notice must be preserved.                              ///
#////                                                                       ///
#//// import/import_transit_demand.py                                       ///
#////                                                                       ///
#////                                                                       ///
#////                                                                       ///
#////                                                                       ///
#//////////////////////////////////////////////////////////////////////////////
#
# Imports the transit demand generated from an iteration of the disaggregate 
# demand models (CT-RAMP) in preparation for the transit assignment
# 
# Note the matrix name mapping from the OMX file names to the Emme database names.
#
# Inputs:
#    output_dir: output directory to read the OMX files from
#    scenario: transit scenario to use for reference zone system
#
# Files referenced:
#    Note: pp is time period, one of EA, AM, MD, PM, EV
#    output/tranTrips_pp.omx
#    output/tranCrossBorderTrips_pp.omx
#    output/tranAirportTrips_pp.omx
#    output/tranVisitorTrips_pp.omx
#    output/tranInternalExternalTrips_pp.omx
#
# Matrix results:
#    Note: pp is time period, one of EA, AM, MD, PM, EV
#    pp_WLKBUS, pp_WLKLRT, pp_WLKCMR, pp_WLKEXP, pp_WLKBRT, 
#    pp_PNRBUS, pp_PNRLRT, pp_PNRCMR, pp_PNREXP, pp_PNRBRT, 
#    pp_KNRBUS, pp_KNRLRT, pp_KNRCMR, pp_KNREXP, pp_KNRBRT
#
# Script example:
"""
    import os
    modeller = inro.modeller.Modeller()
    main_directory = os.path.dirname(os.path.dirname(modeller.desktop.project.path))
    output_dir = os.path.join(main_directory, "output")
    scenario = modeller.scenario
    import_transit_demand = modeller.tool("sandag.model.import.import_transit_demand")
    import_transit_demand(output_dir, scenario)
"""


TOOLBOX_ORDER = 14


import inro.modeller as _m
import inro.emme.matrix as _matrix
import traceback as _traceback
import os


dem_utils = _m.Modeller().module('sandag.utilities.demand')
gen_utils = _m.Modeller().module("sandag.utilities.general")


class ImportMatrices(_m.Tool(), gen_utils.Snapshot):

    output_dir = _m.Attribute(unicode)
    
    tool_run_msg = ""

    @_m.method(return_type=_m.UnicodeType)
    def tool_run_msg_status(self):
        return self.tool_run_msg

    def __init__(self):
        project_dir = os.path.dirname(_m.Modeller().desktop.project.path)
        main_dir = os.path.dirname(project_dir)
        self.output_dir = os.path.join(main_dir, "output")
        self.attributes = ["output_dir"]

    def page(self):
        pb = _m.ToolPageBuilder(self)
        pb.title = "Import transit demand"
        pb.description = """ 
<div style="text-align:left">    
    Imports the trip matrices generated by CT-RAMP in OMX format. <br>
    A total of 25 OMX files are expected, for 5 time periods
    EA, AM, MD, PM and EV, with matrices by 3 model segments and 3 access modes:
    <ul>
        <li>tranTrips_pp.omx</li>
        <li>tranCrossBorderTrips_pp.omx</li>
        <li>tranAirportTrips_pp.omx</li>
        <li>tranVisitorTrips_pp.omx</li>
        <li>tranInternalExternalTrips_pp.omx</li>
    </ul>
</div>
        """
        pb.branding_text = "- SANDAG - Model"

        if self.tool_run_msg != "":
            pb.tool_run_status(self.tool_run_msg_status)
        pb.add_select_file('output_dir', 'directory',
                           title='Select output directory')
        return pb.render()

    def run(self):
        self.tool_run_msg = ""
        try:
            scenario = _m.Modeller().scenario
            self(self.output_dir, scenario)
            run_msg = "Tool completed"
            self.tool_run_msg = _m.PageBuilder.format_info(run_msg, escape=False)
        except Exception as error:
            self.tool_run_msg = _m.PageBuilder.format_exception(
                error, _traceback.format_exc(error))
            raise

    @_m.logbook_trace("Create TOD transit trip tables", save_arguments=True)
    def __call__(self, output_dir, scenario):
        attributes = {"output_dir": output_dir}
        gen_utils.log_snapshot("Sum demand", str(self), attributes)

        self.scenario = scenario
        self.output_dir = output_dir
        self.import_transit_trips()

    @_m.logbook_trace("Import CT-RAMP transit trips from OMX")
    def import_transit_trips(self):
        emmebank = self.scenario.emmebank
        emme_zones = self.scenario.zone_numbers
        matrix_name_tmplts = [
            ("mf%s_%sBUS",    "%s_SET_set1_%s"),
            ("mf%s_%sALL",    "%s_SET_set2_%s"), 
            ("mf%s_%sALLPEN", "%s_SET_set3_%s")
        ]
        periods = ["EA", "AM", "MD", "PM", "EV"]
        access_modes = ["WLK", "PNR", "KNR"]
        matrix_names = []
        for period in periods:
            for acc_mode in access_modes:
                for emme_name, omx_name in matrix_name_tmplts:
                    matrix_names.append(
                        (period, emme_name % (period, acc_mode), omx_name % (acc_mode, period)))
        with gen_utils.OMXManager(self.output_dir, "tran%sTrips_%s.omx") as omx_manager:
            for period, matrix_name, omx_key in matrix_names:
                logbook_label = "Report on import from OMX key %s to matrix %s" % (omx_key, matrix_name)
                visitor_demand = omx_manager.lookup(("Visitor", period), omx_key)
                cross_border_demand = omx_manager.lookup(("CrossBorder", period), omx_key)
                airport_demand = omx_manager.lookup(("Airport", period), omx_key)
                person_demand = omx_manager.lookup(("", period), omx_key)
                internal_external_demand = omx_manager.lookup(("InternalExternal", period), omx_key)
                total_ct_ramp_trips = (
                    visitor_demand + cross_border_demand + airport_demand 
                    + person_demand + internal_external_demand)

                # Check the OMX zones are the same Emme database, assume all files have the same zones
                omx_zones = omx_manager.zone_list("tranTrips_%s.omx" % period)
                if omx_zones != emme_zones:
                    matrix_data = _matrix.MatrixData(type='f', indices=[omx_zones, omx_zones])
                    matrix_data.from_numpy(total_ct_ramp_trips)
                    expanded_matrix_data = matrix_data.expand([emme_zones, emme_zones])
                    matrix = emmebank.matrix(matrix_name)
                    matrix.set_data(expanded_matrix_data, self.scenario)
                else:
                    matrix.set_numpy_data(total_ct_ramp_trips, self.scenario)
                
                dem_utils.demand_report([
                    ("person_demand", person_demand), 
                    ("internal_external_demand", internal_external_demand), 
                    ("cross_border_demand", cross_border_demand),
                    ("airport_demand", airport_demand), 
                    ("visitor_demand", visitor_demand), 
                    ("total_ct_ramp_trips", total_ct_ramp_trips)
                ], logbook_label, self.scenario)
