from simple_compare import is_html_changed

html1 = "<html><body>Hello</body></html>"
html2 = "<html><body>Hello</body></html>"
html3 = "<html><body>Hello!</body></html>"

print("동일한 HTML 비교")
print("is_html_changed:", is_html_changed(html1, html2))  # False

print("\n다른 HTML 비교")
print("is_html_changed:", is_html_changed(html1, html3))  # True 