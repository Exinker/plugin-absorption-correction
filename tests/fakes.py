from collections.abc import Mapping

from plugin.dto import AtomDatum


class HeadlessCorrectionPreview:

    def show(
        self,
        data: Mapping[str, AtomDatum],
        update_callback,
        dump_callback,
    ) -> None:
        for column_id, datum in data.items():
            update_callback(
                column_id=column_id,
                frame=datum.frame,
                bounds=datum.bounds,
            )
