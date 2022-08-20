from datetime import datetime
from meteostat import Hourly
from numpy import datetime64
import pulire as pu
from pulire.validator import ValidationError


df = Hourly("10637", datetime(2018, 1, 1), datetime(2018, 1, 1, 23, 59)).fetch()

myschema = pu.Schema(
    [pu.Index("time", datetime64)],
    [
        pu.Column(
            "temp", float, [pu.validators.minimum(-100), pu.validators.maximum(65)]
        ),
        pu.Column(
            "prcp", float, [pu.validators.minimum(0), pu.validators.maximum(350)]
        ),
        pu.Column(
            "snow", float, [pu.validators.minimum(0), pu.validators.maximum(11000)]
        ),
        pu.Column(
            "wdir", float, [pu.validators.minimum(0), pu.validators.maximum(360)]
        ),
        pu.Column(
            "wspd", float, [pu.validators.minimum(0), pu.validators.maximum(250)]
        ),
        pu.Column(
            "wpgt",
            float,
            [
                pu.validators.minimum(0),
                pu.validators.maximum(500),
                pu.validators.greater("wspd"),
            ],
        ),
        pu.Column("tsun", int, [pu.validators.minimum(0), pu.validators.maximum(60)]),
        pu.Column("srad", int, [pu.validators.minimum(0), pu.validators.maximum(1368)]),
        pu.Column(
            "pres", float, [pu.validators.minimum(850), pu.validators.maximum(1090)]
        ),
        pu.Column("rhum", int, [pu.validators.minimum(0), pu.validators.maximum(100)]),
        pu.Column("cldc", int, [pu.validators.minimum(0), pu.validators.maximum(100)]),
        pu.Column("vsby", int, [pu.validators.minimum(0), pu.validators.maximum(9999)]),
        pu.Column("coco", int, [pu.validators.minimum(1), pu.validators.maximum(27)]),
    ],
)


try:
    myschema.debug(df)
except ValidationError as error:
    print(error.errors)


validated_df = myschema.validate(df)

print(validated_df)
