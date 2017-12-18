#//////////////////////////////////////////////////////////////////////////////
#////                                                                       ///
#//// Copyright INRO, 2016-2017.                                            ///
#//// Rights to use and modify are granted to the                           ///
#//// San Diego Association of Governments and partner agencies.            ///
#//// This copyright notice must be preserved.                              ///
#////                                                                       ///
#//// import/import_traffic_demand.py                                       ///
#////                                                                       ///
#////                                                                       ///
#////                                                                       ///
#////                                                                       ///
#//////////////////////////////////////////////////////////////////////////////
# 
# Imports the auto demand matrices generated from an iteration of the disaggregate 
# demand models (CT-RAMP) and adds the saved disaggregated demand matrices to 
# generate the total auto demand in preparation for the auto assignment.
# 
# Note the matrix name mapping from the OMX file names to the Emme database names.
#
# Inputs:
#    external_zones: set of external zone IDs as a range "1-12"
#    output_dir: output directory to read the OMX files from
#    num_processors: number of processors to use in the matrix calculations 
#    scenario: traffic scenario to use for reference zone system
#
# Files referenced:
#    Note: pp is time period, one of EA, AM, MD, PM, EV, vot is one of low, med, high
#    output/autoInternalExternalTrips_pp_vot.omx
#    output/autoVisitorTrips_pp_vot.omx
#    output/autoCrossBorderTrips_pp_vot.omx
#    output/autoAirportTrips_pp_vot.omx
#    output/autoTrips_pp_vot.omx
#    output/TripMatrices.csv
#
# Matrix inputs:
#    pp_SOVGP_EIWORK, pp_SOVGP_EINONWORK, pp_SOVTOLL_EIWORK, pp_SOVTOLL_EINONWORK,
#    pp_HOV2HOV_EIWORK, pp_HOV2HOV_EINONWORK, pp_HOV2TOLL_EIWORK, pp_HOV2TOLL_EINONWORK,
#    pp_HOV3HOV_EIWORK, pp_HOV3HOV_EINONWORK, pp_HOV3TOLL_EIWORK, pp_HOV3TOLL_EINONWORK
#    pp_SOVGP_EETRIPS, pp_HOV2HOV_EETRIPS, pp_HOV3HOV_EETRIPS
#
# Matrix results:
#    Note: pp is time period, one of EA, AM, MD, PM, EV, V is one of L, M, H
#    pp_SOVGPV, pp_SOVTOLLV, pp_HOV2HOVV, pp_HOV2TOLLV, pp_HOV3HOVV, pp_HOV3TOLLV
#
# Script example:
"""
    import os
    modeller = inro.modeller.Modeller()
    main_directory = os.path.dirname(os.path.dirname(modeller.desktop.project.path))
    output_dir = os.path.join(main_directory, "output")
    external_zones = "1-12"
    num_processors = "MAX-1"
    base_scenario = modeller.scenario
    import_auto_demand = modeller.tool("sandag.model.import.import_auto_demand")
    import_auto_demand(external_zones, output_dir, num_processors, base_scenario)
"""

TOOLBOX_ORDER = 13


import inro.modeller as _m
import traceback as _traceback
import csv as _csv
import os


dem_utils = _m.Modeller().module('sandag.utilities.demand')
gen_utils = _m.Modeller().module("sandag.utilities.general")


class ImportMatrices(_m.Tool(), gen_utils.Snapshot):

    external_zones = _m.Attribute(str)
    output_dir = _m.Attribute(unicode)
    num_processors = _m.Attribute(str)
    
    tool_run_msg = ""

    @_m.method(return_type=_m.UnicodeType)
    def tool_run_msg_status(self):
        return self.tool_run_msg

    def __init__(self):
        self.external_zones = "1-12"
        project_dir = os.path.dirname(_m.Modeller().desktop.project.path)
        main_dir = os.path.dirname(project_dir)
        self.output_dir = os.path.join(main_dir, "output")
        self.num_processors = "MAX-1"
        self.attributes = ["external_zones", "output_dir", "num_processors"]

    def page(self):
        pb = _m.ToolPageBuilder(self)
        pb.title = "Import auto demand and sum matrices"
        pb.description = """ 
<div style="text-align:left">    
    Imports the trip matrices generated by CT-RAMP in OMX format, 
    the commercial vehicle demand in CSV format, 
    and adds the demand from the aggregate models for the final
    trip assignments. <br>
    A total of 25 OMX files are expected, for 5 time periods
    EA, AM, MD, PM and EVm, with matrices by mode and toll / GP-only:
    <ul>
        <li>autoInternalExternalTrips_pp.omx</li>
        <li>autoVisitorTrips_pp.omx</li>
        <li>autoCrossBorderTrips_pp.omx</li>
        <li>autoAirportTrips_pp.omx</li>
        <li>autoTrips_pp.omx</li>
    </ul>
    As well as one CSV file "TripMatrices.csv" for the commercial vehicle trips.
    Adds the aggregate demand from the
    external-external and external-internal demand matrices:
    <ul>
        <li>pp_SOVGP_EETRIPS, pp_HOV2HOV_EETRIPS, pp_HOV3HOV_EETRIPS</li>
        <li>pp_SOVGP_EIWORK, pp_SOVGP_EINONWORK, pp_SOVTOLL_EIWORK, pp_SOVTOLL_EINONWORK</li>
        <li>pp_HOV2HOV_EIWORK, pp_HOV2HOV_EINONWORK, pp_HOV2TOLL_EIWORK, pp_HOV2TOLL_EINONWORK</li>
        <li>pp_HOV3HOV_EIWORK, pp_HOV3HOV_EINONWORK, pp_HOV3TOLL_EIWORK, pp_HOV3TOLL_EINONWORK</li>
    </ul>
    to the time-of-day total demand matrices.
    <br>
</div>
        """
        pb.branding_text = "- SANDAG - Model"

        if self.tool_run_msg != "":
            pb.tool_run_status(self.tool_run_msg_status)
        pb.add_select_file('output_dir', 'directory',
                           title='Select output directory')
        pb.add_text_box("external_zones", title="External zones:")
        dem_utils.add_select_processors("num_processors", pb, self)
        return pb.render()

    def run(self):
        self.tool_run_msg = ""
        try:
            scenario = _m.Modeller().scenario
            self(self.output_dir, self.external_zones, self.num_processors, scenario)
            run_msg = "Tool completed"
            self.tool_run_msg = _m.PageBuilder.format_info(run_msg, escape=False)
        except Exception as error:
            self.tool_run_msg = _m.PageBuilder.format_exception(
                error, _traceback.format_exc(error))
            raise

    @_m.logbook_trace("Create TOD auto trip tables", save_arguments=True)
    def __call__(self, output_dir, external_zones, num_processors, scenario):
        attributes = {
            "output_dir": output_dir, 
            "external_zones": external_zones, 
            "num_processors": num_processors}
        gen_utils.log_snapshot("Create TOD auto trip tables", str(self), attributes)

        self.scenario = scenario
        self.output_dir = output_dir
        self.external_zones = external_zones
        self.num_processors = num_processors
        #self.import_traffic_trips()
        self.import_commercial_vehicle_demand()
        self.add_aggregate_demand()

    @_m.logbook_trace("Import CT-RAMP traffic trips from OMX")
    def import_traffic_trips(self):
        emmebank = self.scenario.emmebank
        periods = ["EA", "AM", "MD", "PM", "EV"]
        matrix_name_tmplts = [
            ("mf%s_SOVGP%s",    "SOV_GP_%s"),
            ("mf%s_SOVTOLL%s",  "SOV_PAY_%s"),
            ("mf%s_HOV2HOV%s",  "SR2_NOPAY_%s"),
            ("mf%s_HOV2TOLL%s", "SR2_PAY_%s"),
            ("mf%s_HOV3HOV%s",  "SR3_NOPAY_%s"),
            ("mf%s_HOV3TOLL%s", "SR3_PAY_%s")]
        omx_file_names = [
            "Trips", "InternalExternalTrips", "VisitorTrips", 
            "CrossBorderTrips", "VisitorTrips", "AirportTrips"]
        matrix_names = []
        for vot_bin in ["low", "med", "high"]:
            vot = vot_bin[0].upper()
            for period in periods:
                for emme_name, omx_name in matrix_name_tmplts:
                    matrix_names.append((period, vot_bin, emme_name % (period, vot), omx_name % (period)))
        with gen_utils.OMXManager(self.output_dir, "auto%sTrips_%s_%s.omx") as omx_manager:
            for period, vot_bin, matrix_name, omx_key in matrix_names:
                logbook_label = "Import from OMX key %s to matrix %s" % (omx_key, matrix_name)
                visitor_demand = omx_manager.lookup(("Visitor", period, vot_bin), omx_key)
                cross_border_demand = omx_manager.lookup(("CrossBorder", period, vot_bin), omx_key)
                airport_demand = omx_manager.lookup(("Airport", period, vot_bin), omx_key)
                person_demand = omx_manager.lookup(("", period, vot_bin), omx_key)
                internal_external_demand = omx_manager.lookup(("InternalExternal", period, vot_bin), omx_key)
                total_ct_ramp_trips = (
                    visitor_demand + cross_border_demand + airport_demand
                    + person_demand + internal_external_demand)
                matrix = emmebank.matrix(matrix_name)
                matrix.set_numpy_data(total_ct_ramp_trips, self.scenario)
                dem_utils.demand_report([
                    ("person_demand", person_demand),
                    ("internal_external_demand", internal_external_demand),
                    ("cross_border_demand", cross_border_demand),
                    ("airport_demand", airport_demand),
                    ("visitor_demand", visitor_demand),
                    ("total_ct_ramp_trips", total_ct_ramp_trips)
                ], logbook_label, self.scenario)

    @_m.logbook_trace('Import commercial vehicle demand')
    def import_commercial_vehicle_demand(self):
        scenario = self.scenario
        emmebank = scenario.emmebank
        name_map = {}
        periods = ["EA", "AM", "MD", "PM", "EV"]
        for period in periods:
            for cvm_acc, access_type in [("T", "TOLL"), ("NT", "GP")]:
                name_map["CVM_%s:L%s" % (period, cvm_acc)] = ("%s_SOV%sH" % (period, access_type), 1.0)
                name_map["CVM_%s:M%s" % (period, cvm_acc)] = ("%s_TRKM%s" % (period, access_type), 1.5)
                name_map["CVM_%s:H%s" % (period, cvm_acc)] = ("%s_TRKH%s" % (period, access_type), 2.5)
        matrices = [(k,emmebank.matrix(v).get_numpy_data(scenario), pce) for k,(v, pce) in name_map.iteritems()]
        
        path = os.path.join(self.output_dir, "TripMatrices.csv")
        with open(path, 'r') as f:
            reader = _csv.reader(f)
            header = reader.next()
            i_row = header.index("i")
            j_row = header.index("j")
            array_index = []
            for key, array, pce in matrices:
                array_index.append((array, header.index(key)))
            for row in reader:
                p, q = int(row[i_row]) - 1, int(row[j_row]) - 1
                for array, ref_index in array_index:
                    array[p][q] += float(row[ref_index])
        for key, array, pce in matrices:
            matrix = emmebank.matrix(name_map[key][0])
            if pce != 1.0:
                array = array * pce
            matrix.set_numpy_data(array, scenario)

    @_m.logbook_trace('Add aggregate demand')
    def add_aggregate_demand(self):
        matrix_calc = dem_utils.MatrixCalculator(self.scenario, self.num_processors)
        periods = ["EA", "AM", "MD", "PM", "EV"]
        vots = ["L", "M", "H"]
        # with matrix_calc.trace_run("Add commercial vehicle trips to auto demand"):
        #     for period in periods:
        #         for vot in vots:
        #             # Segment imported demand into 3 equal parts for VOT Low/Med/High
        #             matrix_calc.add(
        #                 "mf%s_SOVGP%s" % (period, vot), 
        #                 "mf%(p)s_SOVGP%(v)s + (1.0/3.0)*mf%(p)s_COMVEHGP_import" % ({'p': period, 'v': vot}))
        #             matrix_calc.add(
        #                 "mf%s_SOVTOLL%s" % (period, vot), 
        #                 "mf%(p)s_SOVTOLL%(v)s + (1.0/3.0)*mf%(p)s_COMVEHTOLL_import" % ({'p': period, 'v': vot}))

        with matrix_calc.trace_run("Add external-internal trips to auto demand"):
            modes = ["SOVGP", "SOVTOLL", "HOV2HOV", "HOV2TOLL", "HOV3HOV", "HOV3TOLL"]
            for period in periods:
                for mode in modes:
                    for vot in vots:
                        # Segment imported demand into 3 equal parts for VOT Low/Med/High
                        matrix_calc.add("mf%s_%s%s" % (period, mode, vot),
                             "mf%(p)s_%(m)s%(v)s "
                             "+ (1.0/3.0)*mf%(p)s_%(m)s_EIWORK "
                             "+ (1.0/3.0)*mf%(p)s_%(m)s_EINONWORK" % ({'p': period, 'm': mode, 'v': vot}))

        # External - external faster with single-processor as number of O-D pairs is so small (12 X 12)
        matrix_calc.num_processors = 0
        with matrix_calc.trace_run("Add external-external trips to auto demand"):
            modes = ["SOVGP", "HOV2HOV", "HOV3HOV"]
            for period in periods:
                for mode in modes:
                    for vot in vots:
                        # Segment imported demand into 3 equal parts for VOT Low/Med/High
                        matrix_calc.add(
                            "mf%s_%s%s" % (period, mode, vot),
                            "mf%(p)s_%(m)s%(v)s + (1.0/3.0)*mf%(p)s_%(m)s_EETRIPS" % ({'p': period, 'm': mode, 'v': vot}),
                            {"origins": self.external_zones, "destinations": self.external_zones})
