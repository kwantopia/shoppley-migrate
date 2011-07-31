package com.higherpass.android.ContactAPI;

import java.util.ArrayList;

import android.content.ContentResolver;
import android.content.Intent;
import android.database.Cursor;
import android.net.Uri;
import android.os.Build;

import com.higherpass.android.ContactAPI.objects.Address;
import com.higherpass.android.ContactAPI.objects.ContactList;
import com.higherpass.android.ContactAPI.objects.Email;
import com.higherpass.android.ContactAPI.objects.IM;
import com.higherpass.android.ContactAPI.objects.Organization;
import com.higherpass.android.ContactAPI.objects.Phone;

public abstract class ContactAPI {

	private static ContactAPI api;

	private Cursor cur;
	private ContentResolver cr;
	protected ContactList contacts = null;

	public Uri CONTENT_URI;
	public String DISPLAY_NAME;
	public String _ID;

	public ContactList getContactList() {
		return contacts;
	}

	public static ContactAPI getAPI() {
		if (api == null) {
			String apiClass;
			if (Integer.parseInt(Build.VERSION.SDK) >= Build.VERSION_CODES.ECLAIR) {
				apiClass = "com.higherpass.android.ContactAPI.ContactAPISdk5";
			} else {
				apiClass = "com.higherpass.android.ContactAPI.ContactAPISdk3";
			}

			try {
				Class<? extends ContactAPI> realClass = Class.forName(apiClass)
						.asSubclass(ContactAPI.class);
				api = realClass.newInstance();
			} catch (Exception e) {
				throw new IllegalStateException(e);
			}

		}
		return api;
	}

	public abstract Intent getContactIntent();

	public abstract ContactList newContactList();

	public abstract Cursor getCur();

	public abstract void setCur(Cursor cur);

	public abstract ContentResolver getCr();

	public abstract void setCr(ContentResolver cr);

	public abstract ArrayList<Phone> getPhoneNumbers(String id);

	public abstract ArrayList<Email> getEmailAddresses(String id);

	public abstract ArrayList<Address> getContactAddresses(String id);

	public abstract ArrayList<IM> getIM(String id);

	public abstract Organization getContactOrg(String id);

	public abstract void newContactList(Callback callback);
}