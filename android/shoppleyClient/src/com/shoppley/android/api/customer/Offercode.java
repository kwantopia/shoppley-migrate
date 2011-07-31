package com.shoppley.android.api.customer;

import com.google.gson.annotations.SerializedName;

public class Offercode{
	@SerializedName("offer_code_id")
	public String offer_code_id;
	@SerializedName("description")
	public String description;
	@SerializedName("img")
	public String img;
	@SerializedName("address1")
	public String address1;
	@SerializedName("offer_id")
	public String offer_id;
	@SerializedName("expires")
	public String expires;
	@SerializedName("lon")
	public String lon;
	@SerializedName("name")
	public String name;
	@SerializedName("phone")
	public String phone;
	@SerializedName("code")
	public String code;
	@SerializedName("expires_time")
	public String expires_time;
	@SerializedName("citystatezip")
	public String citystatezip;
	@SerializedName("lat")
	public String lat;
	@SerializedName("banner")
	public String banner;
	@SerializedName("merchant_name")
	public String merchant_name;
}