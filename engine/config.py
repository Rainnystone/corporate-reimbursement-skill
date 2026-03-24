# reimbursement/config.py

# Mapping of Purchaser Name headers to Output Excel file suffixes
# USAGE: Fill these with your actual company names for local execution.
HEADERS = {
    "BJ": "CORPORATE_ENTITY_BJ_NAME",
    "SH": "CORPORATE_ENTITY_SH_NAME"
}

# Excel structure mapping based on the provided blank template
EXCEL_MAPPING = {
    "sheets": {
        "付款申请表（面单）": {"description": "Cover page"},
        "国内差旅详单": {
            "categories": {
                "住宿费": {"start_row": 4, "max_rows": 6},
                "餐费": {"start_row": 13, "max_rows": 8},
                "其它费用": {"start_row": 23, "max_rows": 5}
            }
        },
        "国内交通详单（1）": {
            "categories": {
                "一、 纸质普通发票及非实名制票据": {"start_row": 3, "max_rows": 5},
                "二、航空运输电子客票行程单": {"start_row": 11, "max_rows": 12}
            }
        },
        "国内交通详单（2）": {
            "categories": {
                "滴滴费用": {"start_row": 2, "max_rows": 4},
                "四、铁路车票": {"start_row": 9, "max_rows": 11},
                "五、公路水路等其他客票": {"start_row": 22, "max_rows": 6}
            }
        },
        "国际差旅详单": {}
    }
}
