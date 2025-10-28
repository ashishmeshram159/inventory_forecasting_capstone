

# import sqlite3
# con = sqlite3.connect("data/db_files/inventory.db")

# rows = con.execute("""
#     SELECT DISTINCT [Product ID], [Store ID], Date
#     FROM inventory
#     WHERE [Product ID] = 'T0002'
#     LIMIT 10
# """).fetchall()

# for r in rows:
#     print(r)


from tools.db_tools import get_product_context_with_month, get_category_context_with_month, get_overall_category_summary
# print('\n\n')
# print(get_product_context_with_month(product_id="T0002", store_id="S001",  month_name="January")) 
# print('\n\n')
# print(get_product_context_with_month(product_id="T0002", month_name="January"))
# print('\n\n')
# print(get_product_context_with_month(product_id="T0002", store_id="S001"))
# print('\n\n')
# print(get_product_context_with_month(product_id="T0002"))
# print('\n\n')

# # print(predict_demand("T0002", "S0001", "2022-01-01 00:00:00"))


# print('\n\n')
# print(get_category_context("Toys", "S002"))
# print('\n\n')
# print(get_category_context("Toys"))
# print('\n\n')



# print('\n\n')
# print(get_category_context_with_month(category="Toys", store_id="S001",  month_name="January"))
# print('\n\n')
# # print(get_category_context_with_month(category="Toys", month_name="January"))
# # print('\n\n')
# # print(get_category_context_with_month(category="Toys", store_id="S001"))
# # print('\n\n')
# print(get_category_context_with_month(category="Toys"))
# print('\n\n')

# print('\n\n')
print(get_overall_category_summary(store_id="S001",  month_name="January"))
# print('\n\n')
# print(get_overall_category_summary(store_id="S001"))
# print('\n\n')
# print(get_overall_category_summary(month_name="January"))
# print('\n\n')

# from RAG.rag_utility import query_promotional_offers
# result = query_promotional_offers("What are the offers available for electronics?")
# print(result)