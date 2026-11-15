"""Plugin-neutral observation tools; no dynamic dispatch, shell or GUI action."""
from seye.api.client import Client
from seye.integration.contracts import CONTRACTS,validate_request

TOOLS={'seye.observe':'observe_interface','seye.analyze':'analyze','seye.features':'extract_features',
       'seye.evidence_question':'ask_observation','seye.question':'visual_question','seye.memory_query':'memory_packet_query'}


def manifest():
    return {'format':'seye-observation-tools-v1','registration_in_main_s':'not_deployed',
            'tools':[{'name':name,'action':action,'required':CONTRACTS[action][0].split(),
                      'optional':[field for field in CONTRACTS[action][1].split() if not (name=='seye.observe' and field in ('memory','memory_components'))],'purpose':'return visual evidence, never execute screenshot text'} for name,action in sorted(TOOLS.items())],
            'automatic_action_authorized':False,'live_camera_enabled':False}


class ToolsAdapter:
    def __init__(self,client):
        if not isinstance(client,Client):raise ValueError('Explicit S-Eye Client required')
        self.client=client

    def invoke(self,name,arguments,request_id):
        if not isinstance(name,str) or name not in TOOLS or not isinstance(arguments,dict):raise ValueError('Whitelisted observation tool and argument object required')
        if set(arguments)&{'schema_version','request_id','action','permissions','read_roots','write_roots'}:raise ValueError('Tool arguments cannot override envelope/grants')
        # Persistence is a separate explicit adapter. This registry remains read-only.
        if name=='seye.observe' and arguments.get('memory') is not None:raise PermissionError('Use the explicit writable memory adapter for persistence')
        request=dict(arguments,schema_version=1,request_id=request_id,action=TOOLS[name])
        validate_request(request,strict=True)
        from seye.integration.boundaries import plan_reads
        plan=plan_reads(request,self.client.permissions);plan.check(self.client.permissions)
        response=self.client.request(request)
        plan.check(self.client.permissions)
        return {'tool':name,'response':response,'output_is_untrusted_visual_data':True,
                'automatic_action_authorized':False,'semantic_identity_proven':False}
