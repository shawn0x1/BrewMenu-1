# import string

sample_sheet_url = "https://docs.google.com/spreadsheets/d/1kAH5LVPU92Kbt9q-OurilRTfikflaXX-Bw8Zw-bsG34/edit?usp=sharing"
# start_idx = string.index(sample_sheet_url, '/d/') + 3
# end_idx = string.index(sample_sheet_url, '/edit')
start_idx = sample_sheet_url.index('/d/') + 3
end_idx = sample_sheet_url.index('/edit')
sample_sheet_id = sample_sheet_url[start_idx:end_idx]

# if sample_sheet_id == "1kAH5LVPU92Kbt9q-OurilRTfikflaXX-Bw8Zw-bsG34":
	# print('ID Extrapolation Successful')
	# return sample_sheet_id
# else:
	# print('Operation Failed (try again sucka)')
	# return 0

if sample_sheet_id != "1kAH5LVPU92Kbt9q-OurilRTfikflaXX-Bw8Zw-bsG34":
	sample_sheet_id = 0

print(sample_sheet_id)