from nautobot.core.jobs import Job, BooleanVar, FileVar, ObjectVar
from nautobot.dcim.models import Location, LocationType
from nautobot.extras.models import Status

name = "CSV Locations"

class CSVImportJob(Job):
    """Job to import locations from a CSV file."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.job_results = {
            "created": 0,
            "errors": 0,
        }


    class Meta:
        """Job metadata."""

        name = "CSV Import Locations"
        description = "Import locations from a CSV file"
    
    debug = BooleanVar(description="Enable debug mode", default=False)

    csv_file = FileVar(description="CSV file containing locations to import")

    location_status = ObjectVar(model=Status, query_params={"content_types": "dcim.location"})

    def parse_site_type(self, site_name):
        pass

    def run(self, csv_file, debug, location_status, *args, **kwargs):
        """Run the job."""
        pass
        