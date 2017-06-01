#//////////////////////////////////////////////////////////////////////////////
#////                                                                       ///
#//// Copyright INRO, 2016-2017.                                            ///
#//// Rights to use and modify are granted to the                           ///
#//// San Diego Association of Governments and partner agencies.            ///
#//// This copyright notice must be preserved.                              ///
#////                                                                       ///
#//// model/commercial_vehicle/generation.py                                ///
#////                                                                       ///
#////                                                                       ///
#////                                                                       ///
#////                                                                       ///
#//////////////////////////////////////////////////////////////////////////////

TOOLBOX_ORDER = 52



import inro.modeller as _m
import traceback as _traceback

import pandas as pd
import os


class CommercialVehicleDistribution(_m.Tool()):

    input_directory = _m.Attribute(str)

    tool_run_msg = ""

    @_m.method(return_type=_m.UnicodeType)
    def tool_run_msg_status(self):
        return self.tool_run_msg

    def __init__(self):
        project_dir = os.path.dirname(_m.Modeller().desktop.project.path)
        self.input_directory = os.path.join(os.path.dirname(project_dir), "input")

    def page(self):
        # Equivalent to commVehGen.rsc
        pb = _m.ToolPageBuilder(self)
        pb.title = "Commercial Vehicle Generation"
        pb.description = """
<div style="text-align:left">
    Calculate commerical vehicle productions and attractions
    based on mgra13_based_input2012.csv.
    The very small truck generation model is based on the Phoenix 
    four-tire truck model documented in the TMIP Quick Response Freight Manual. 

    Linear regression models generate trip ends, balancing attractions to productions.
    <br>
    Input: MGRA file in CSV format with the following fields: 
    <ul>
    <li>
        (a) TOTEMP, total employment (same regardless of classification system); 
    </li><li>
        (b) RETEMPN, retail trade employment per the NAICS classification system;               
    </li><li>
        (c) FPSEMPN, financial and professional services employment per the NAICS classification system; 
    </li><li>
        (d) HEREMPN, health, educational, and recreational employment per the NAICS classification system; 
    </li><li>
        (e) OTHEMPN, other employment per the NAICS classification system; 
    </li><li>
        (f) AGREMPN, agricultural employmentper the NAICS classificatin system; 
    </li><li>
        (g) MWTEMPN, manufacturing, warehousing, and transportation emp;loyment per the NAICS classification system; and, 
    </li><li>
        (h) TOTHH, total households.
    </li></ul>
    <br>
    Output: Trip productions and attractions in matrices 'moCOMMVEH_PROD' and 'mdCOMMVEH_ATTR' respectively.
</div>
        """

        pb.branding_text = "- SANDAG - Model - Commercial vehicle"
        if self.tool_run_msg != "":
            pb.tool_run_status(self.tool_run_msg_status)

        pb.add_select_file('input_directory', 'directory',
                           title='Select input directory')

        return pb.render()

    def run(self):
        self.tool_run_msg = ""
        try:
            scenario = _m.Modeller().scenario
            self(self.input_directory, scenario)
            run_msg = "Tool complete"
            self.tool_run_msg = _m.PageBuilder.format_info(run_msg, escape=False)
        except Exception as error:
            self.tool_run_msg = _m.PageBuilder.format_exception(
                error, _traceback.format_exc(error))
            raise

    @_m.logbook_trace('Commercial vehicle generation')
    def __call__(self, input_directory, scenario):        
        utils = _m.Modeller().module('sandag.utilities.demand')
        emmebank = scenario.emmebank
        props = utils.Properties(os.path.join(input_directory, "sandag_abm.properties"))

        mgra = pd.read_csv(
            os.path.join(input_directory, 'mgra13_based_input2012.csv'))

        calibration = 1.4

        mgra['RETEMPN'] = mgra.emp_retail + mgra.emp_personal_svcs_retail
        mgra['FPSEMPN'] = mgra.emp_prof_bus_svcs
        mgra['HEREMPN'] = mgra.emp_health + mgra.emp_pvt_ed_k12 \
                          + mgra.emp_pvt_ed_post_k12_oth + mgra.emp_amusement
        mgra['AGREMPN'] = mgra.emp_ag
        mgra['MWTEMPN'] = mgra.emp_const_non_bldg_prod \
                          + mgra.emp_const_bldg_prod + mgra.emp_mfg_prod \
                          + mgra.emp_trans
        mgra['MILITARY'] = mgra.emp_fed_mil
        mgra['TOTEMP'] = mgra.emp_total
        mgra['OTHEMPN'] = mgra.TOTEMP - (mgra.RETEMPN + mgra.FPSEMPN
                                         + mgra.HEREMPN + mgra.AGREMPN
                                         + mgra.MWTEMPN + mgra.MILITARY)
        mgra['TOTHH'] = mgra.hh

        mgra['PROD'] = calibration * (
            0.95409 * mgra.RETEMPN + 0.54333 * mgra.FPSEMPN
            + 0.50769 * mgra.HEREMPN + 0.63558 * mgra.OTHEMPN
            + 1.10181 * mgra.AGREMPN + 0.81576 * mgra.MWTEMPN
            + 0.15000 * mgra.MILITARY + 0.1 * mgra.TOTHH)
        mgra['ATTR'] = mgra.PROD

        # Adjustment to match military CTM trips to match gate counts
        military_ctm_adjustment = props["RunModel.militaryCtmAdjustment"]
        if military_ctm_adjustment:
            mgra_m = pd.read_csv(os.path.join(
                input_directory, 'cvm_military_adjustment.csv'))
            mgra = pd.merge(mgra, mgra_m, on='mgra', how='outer')
            mgra.fillna(1, inplace=True)
            mgra['PROD'] = mgra['PROD'] * mgra['scale']
            mgra['ATTR'] = mgra['ATTR'] * mgra['scale']

        taz = mgra.groupby('taz').sum()
        taz.reset_index(inplace=True)
        taz = utils.add_missing_zones(taz, scenario)
        taz.sort('taz', inplace=True)

        prod = emmebank.matrix('moCOMMVEH_PROD')
        attr = emmebank.matrix('mdCOMMVEH_ATTR')
        prod.set_numpy_data(taz.PROD.values, scenario)
        attr.set_numpy_data(taz.ATTR.values, scenario)

        return taz[['taz', 'PROD', 'ATTR']]

