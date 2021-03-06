# -*- coding: utf-8 -*-
#BEGIN_HEADER
import logging
import os
import uuid
from pprint import pprint as pp

from installed_clients.KBaseReportClient import KBaseReport

from VariationUtil.Util.VariationToVCF import VariationToVCF
from VariationUtil.Util.VCFToVariation import VCFToVariation

from installed_clients.WorkspaceClient import Workspace

#END_HEADER


class VariationUtil:
    '''
    Module Name:
    VariationUtil

    Module Description:
    A KBase module: VariationUtil
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "0.0.1"
    GIT_URL = "https://github.com/kbasecollaborations/VariationUtil"
    GIT_COMMIT_HASH = "5c21f7b209448d534b4f4c1477d027046eb0247b"

    #BEGIN_CLASS_HEADER
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.config = config
     
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.shared_folder = config['scratch']
        logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                            level=logging.INFO)
        #END_CONSTRUCTOR
        pass


    def save_variation_from_vcf(self, ctx, params):
        """
        Save a variation (and trait?) object to Kbase given a reference genome, object output name,
        Variant Call Format (VCF) file, and sample attribute file.
        :param params: instance of type "save_variation_input" (## funcdef
           save_variation_from_vcf ## required input params:
           genome_or_assembly_ref: KBaseGenomes.Genome or
           KBaseGenomeAnnotations.Assembly object reference *** variation
           input data *** vcf_staging_file_path: path to location data
           associated with samples variation_object_name: output name for
           KBase variation object *** sample input data ***
           sample_attribute_ref: x/y/z reference to kbase sample attribute
           optional params: NA output report: report_name report_ref HTML
           visualization: Manhattan plot *** Visualization *** plot_maf:
           generate histogram of minor allele frequencies plot_hwe: generate
           histogram of Hardy-Weinberg Equilibrium p-values) -> structure:
           parameter "workspace_name" of String, parameter
           "genome_or_assembly_ref" of type "obj_ref" (An X/Y/Z style
           reference), parameter "vcf_staging_file_path" of type "filepath"
           (KBase file path to staging files), parameter
           "variation_object_name" of String, parameter
           "sample_attribute_ref" of type "obj_ref" (An X/Y/Z style reference)
        :returns: instance of type "save_variation_output" -> structure:
           parameter "report_name" of String, parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: report
        #BEGIN save_variation_from_vcf
        genome_or_assembly_ref = params['genome_or_assembly_ref']
        ws_url = self.config['workspace-url']
        wsc = Workspace(ws_url)
        obj_type = wsc.get_object_info3({'objects': [{'ref': genome_or_assembly_ref}]})['infos'][0][2]
        if ('KBaseGenomes.Genome' in obj_type):
            params['genome_ref'] = genome_or_assembly_ref
        elif ('KBaseGenomeAnnotations.Assembly' in obj_type):
            params['assembly_ref'] = genome_or_assembly_ref
        else:
          raise ValueError(obj_type + ' is not the right input for this method. Valid input include KBaseGenomes.Genome or KBaseGenomeAnnotations.Assembly ' )


 
        vtv = VCFToVariation(self.config, self.shared_folder, self.callback_url)

        var_obj = vtv.import_vcf(params)
        var_obj_ref = str(var_obj[0][6])+"/"+str(var_obj[0][0])+"/"+str(var_obj[0][4])

        upload_message = "Variation object created."
        upload_message += "\nObject #"+str(var_obj[0][0])
        upload_message += "\nObject name: "+ str(var_obj[0][1])
        upload_message += "\nGenotypes in variation: "+str(var_obj[1]['numgenotypes'])
        upload_message += "\nVariants in VCF file: "+str(var_obj[1]['numvariants'])

        report_obj = {
            'objects_created': [{'ref': var_obj_ref, 'description': 'Variation object from VCF file.'}],
            'text_message': upload_message
        }

        report_client = KBaseReport(self.callback_url)
        report_create = report_client.create({'report': report_obj, 'workspace_name': params['workspace_name']})

        report = {
            "report_name": report_create['name'],
            "report_ref": report_create['ref'],
            "workspace_name": params["workspace_name"]
        }

        #END save_variation_from_vcf

        # At some point might do deeper type checking...
        if not isinstance(report, dict):
            raise ValueError('Method save_variation_from_vcf return value ' +
                             'report is not type dict as required.')
        # return the results
        return [report]

    def export_variation_as_vcf(self, ctx, params):
        """
        Export KBase variation object as Variant Call Format (VCF) file
        :param params: instance of type "export_variation_input" (## funcdef
           export_variation_as_vcf ## required input params: Variation object
           reference optional params: NA output report: Shock id pointing to
           exported vcf file) -> structure: parameter "input_var_ref" of type
           "obj_ref" (An X/Y/Z style reference)
        :returns: instance of type "export_variation_output" -> structure:
           parameter "shock_id" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN export_variation_as_vcf

        vtv = VariationToVCF(self.callback_url, self.shared_folder)
        output = vtv.export_as_vcf(params)

        #END export_variation_as_vcf

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method export_variation_as_vcf return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]

    def get_variation_as_vcf(self, ctx, params):
        """
        Given a reference to a variation object, and output name: return a Variant Call Format (VCF)
        file path and name.
        :param params: instance of type "get_variation_input" (## funcdef
           get_variation_as_vcf ## required input params: Variation object
           reference output file name optional params: NA output report: path
           to returned vcf name of variation object) -> structure: parameter
           "variation_ref" of type "obj_ref" (An X/Y/Z style reference),
           parameter "filename" of String
        :returns: instance of type "get_variation_output" -> structure:
           parameter "path" of type "filepath" (KBase file path to staging
           files), parameter "variation_name" of String
        """
        # ctx is the context object
        # return variables are: file
        #BEGIN get_variation_as_vcf
        vtv = VariationToVCF(self.callback_url, self.shared_folder)
        file = vtv.variation_to_vcf(params)

        #END get_variation_as_vcf

        # At some point might do deeper type checking...
        if not isinstance(file, dict):
            raise ValueError('Method get_variation_as_vcf return value ' +
                             'file is not type dict as required.')
        # return the results
        return [file]
    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
