package com.shoppley.android.api.customer;

import java.io.IOException;

import org.apache.http.HttpResponse;
import org.apache.http.ParseException;
import org.apache.http.util.EntityUtils;
import org.json.JSONException;
import org.json.JSONObject;

import android.util.Log;

import com.shoppley.android.api.ShoppleyAPI;

public class ShoppleyCustomerAPI extends ShoppleyAPI {

	public FeedbackOfferResponse customerFeedbackOffer(String feedback,
			String offer_id) {
		JSONObject obj = new JSONObject();
		try {
			obj.put("feedback", feedback);
			obj.put("offer_id", offer_id);
		} catch (JSONException e) {
			// TODO Auto-generated catch block
		}
		try {
			HttpResponse response = httpPostRequest(
					"/m/customer/offer/feedback/", obj);
			return gson.fromJson(EntityUtils.toString(response.getEntity()),
					FeedbackOfferResponse.class);
		} catch (ParseException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (NullPointerException e) {
			// TODO: handle exception
			e.printStackTrace();
		}
		return null;
	}

	public ForwardOfferResponse customerForwardOffer(String note,
			String offer_code, String contacts) {
		JSONObject obj = new JSONObject();
		try {
			obj.put("note", note);
			obj.put("offer_code", offer_code);
			obj.put("phones", contacts);
		} catch (JSONException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		try {
			HttpResponse response = httpPostRequest(
					"/m/customer/offer/forward/", obj);
			return gson.fromJson(EntityUtils.toString(response.getEntity()),
					ForwardOfferResponse.class);
		} catch (ParseException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (NullPointerException e) {
			// TODO: handle exception
			e.printStackTrace();
		}
		return null;
	}

	public RateOfferResponse customerRateOffer(String offer_code_id,
			String rating) {
		JSONObject obj = new JSONObject();
		try {
			obj.put("offer_code_id", offer_code_id);
			obj.put("rating", rating);
		} catch (JSONException e) {
			// TODO Auto-generated catch block
		}
		try {
			HttpResponse response = httpPostRequest(
					"/m/customer/offer/feedback/", obj);
			return gson.fromJson(EntityUtils.toString(response.getEntity()),
					RateOfferResponse.class);
		} catch (ParseException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (NullPointerException e) {
			// TODO: handle exception
			e.printStackTrace();
		}
		return null;
	}

	public RegisterResponse customerRegister(String email, String password,
			String phone, String zipcode) {
		JSONObject obj = new JSONObject();
		try {
			obj.put("email", email);
			obj.put("password", password);
			obj.put("phone", phone);
			obj.put("zipcode", zipcode);
		} catch (JSONException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		try {
			HttpResponse response = httpPostRequest("/m/customer/register/",
					obj);
			return gson.fromJson(EntityUtils.toString(response.getEntity()),
					RegisterResponse.class);
		} catch (ParseException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (NullPointerException e) {
			// TODO: handle exception
			e.printStackTrace();
		}
		return null;
	}

	public OffercodeResponse customerRequestOfferCode(String offerID){
		JSONObject obj = new JSONObject();
		try {
			obj.put("offer_id", offerID);
		} catch (JSONException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		try {
			HttpResponse response = httpPostRequest(
					"/m/customer/offer/offercode/", obj);
			String d = EntityUtils.toString(response.getEntity());
			return gson.fromJson(d, OffercodeResponse.class);
		} catch (ParseException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (NullPointerException e) {
			// TODO: handle exception
			e.printStackTrace();
		}
		return null;
	}

	public CurrentOfferResponse customerShowOffers(double lat, double lng){
		JSONObject obj = new JSONObject();
		try {
			obj.put("lat", lat);
			obj.put("lon", lng);
		} catch (JSONException e) {
			// TODO Auto-generated catch block
		}
		try {
			HttpResponse response = httpPostRequest(
					"/m/customer/offers/current/", obj);
			String offer = EntityUtils.toString(response.getEntity());
			Log.d("Offer", offer);
			return gson.fromJson(offer, CurrentOfferResponse.class);
		} catch (ParseException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (NullPointerException e) {
			// TODO: handle exception
			e.printStackTrace();
		}
		return null;
	}

	public RedeemedOfferResponse customerShowRedeemedOffers(double lat,
			double lng) {
		JSONObject obj = new JSONObject();
		try {
			obj.put("lat", lat);
			obj.put("lon", lng);
		} catch (JSONException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		try {
			HttpResponse response = httpGetRequest(
					"/m/customer/offers/redeemed/", obj);
			String offer = EntityUtils.toString(response.getEntity());
			Log.d("Redeemed", offer);
			return gson.fromJson(offer, RedeemedOfferResponse.class);
		} catch (ParseException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (NullPointerException e) {
			// TODO: handle exception
			e.printStackTrace();
		}
		return null;
	}

}
