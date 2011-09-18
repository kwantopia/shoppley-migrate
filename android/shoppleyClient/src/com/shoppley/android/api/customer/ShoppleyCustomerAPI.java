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
			obj.put("offer_code_id", offer_id);
		} catch (JSONException e) {
			// TODO Auto-generated catch block
		}
		try {
			HttpResponse response = httpPostRequest(
					"/m/customer/offer/feedback/", obj);
			String responseStr = EntityUtils.toString(response.getEntity());
			Log.d("customerFeedbackOffer", responseStr);
			return gson.fromJson(responseStr, FeedbackOfferResponse.class);
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
			String responseStr = EntityUtils.toString(response.getEntity());
			Log.d("customerForwardOffer", responseStr);
			return gson.fromJson(responseStr, ForwardOfferResponse.class);
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
					"/m/customer/offer/rate/", obj);
			String responseStr = EntityUtils.toString(response.getEntity());
			Log.d("customerRateOffer", responseStr);
			return gson.fromJson(responseStr, RateOfferResponse.class);
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
			HttpResponse response = httpPostRequestNoCookies("/m/customer/register/",
					obj);
			String responseStr = EntityUtils.toString(response.getEntity());
			Log.d("customerRegister", responseStr);
			return gson.fromJson(responseStr, RegisterResponse.class);
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

	public OffercodeResponse customerRequestOfferCode(String offerID) {
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
			String responseStr = EntityUtils.toString(response.getEntity());
			Log.d("customerRequestOfferCode", responseStr);
			return gson.fromJson(responseStr,
					OffercodeResponse.class);
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

	public CurrentOfferResponse customerShowOffers(double lat, double lng) {
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
			String responseStr = EntityUtils.toString(response.getEntity());
			Log.d("customerShowOffers", responseStr);
			return gson.fromJson(responseStr,
					CurrentOfferResponse.class);
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
			HttpResponse response = httpGetRequest(
					"/m/customer/offers/redeemed/", obj);
			String responseStr = EntityUtils.toString(response.getEntity());
			Log.d("customerShowRedeemedOffers", responseStr);
			return gson.fromJson(responseStr,
					RedeemedOfferResponse.class);
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

	public IWantResponse sendIWantMessage(String request) {
		JSONObject obj = new JSONObject();
		try {
			obj.put("request", request);
		} catch (JSONException e) {
			// TODO Auto-generated catch block
		}
		try {
			HttpResponse response = httpPostRequest(
					"/m/customer/iwant/", obj);
			String responseStr = EntityUtils.toString(response.getEntity());
			Log.d("sendIWantMessage", responseStr);
			return gson.fromJson(responseStr,
					IWantResponse.class);
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
