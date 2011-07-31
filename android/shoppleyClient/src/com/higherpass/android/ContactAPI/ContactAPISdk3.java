package com.higherpass.android.ContactAPI;

import java.util.ArrayList;

import android.content.ContentResolver;
import android.content.Intent;
import android.database.Cursor;
import android.provider.Contacts;
import android.provider.ContactsContract;
import android.provider.Contacts.People;

import com.higherpass.android.ContactAPI.objects.Address;
import com.higherpass.android.ContactAPI.objects.Contact;
import com.higherpass.android.ContactAPI.objects.ContactList;
import com.higherpass.android.ContactAPI.objects.Email;
import com.higherpass.android.ContactAPI.objects.IM;
import com.higherpass.android.ContactAPI.objects.Organization;
import com.higherpass.android.ContactAPI.objects.Phone;

public class ContactAPISdk3 extends ContactAPI {

	private Cursor cur;
	private ContentResolver cr;

	public ContactAPISdk3() {
		CONTENT_URI = People.CONTENT_URI;
		DISPLAY_NAME = People.DISPLAY_NAME;
		_ID = People._ID;
	}

	public Cursor getCur() {
		return cur;
	}

	public void setCur(Cursor cur) {
		this.cur = cur;
	}

	public ContentResolver getCr() {
		return cr;
	}

	public void setCr(ContentResolver cr) {
		this.cr = cr;
	}

	public Intent getContactIntent() {
		return (new Intent(Intent.ACTION_PICK, People.CONTENT_URI));
	}

	public ContactList newContactList() {
		contacts = new ContactList();
		String id;

		this.cur = this.cr.query(People.CONTENT_URI, null, null, null, null);
		if (this.cur.getCount() > 0) {
			while (cur.moveToNext()) {
				Contact c = new Contact();
				id = cur.getString(cur.getColumnIndex(People._ID));
				c.setId(id);
				c.setDisplayName(cur.getString(cur
						.getColumnIndex(People.DISPLAY_NAME)));
				if (Integer.parseInt(cur.getString(cur
						.getColumnIndex(People.PRIMARY_PHONE_ID))) > 0) {
					c.setPhone(this.getPhoneNumbers(id));
				}
				c.setEmail(this.getEmailAddresses(id));
				ArrayList<String> notes = new ArrayList<String>();
				notes.add(cur.getString(cur.getColumnIndex(People.NOTES)));
				c.setNotes(notes);
				c.setAddresses(this.getContactAddresses(id));
				c.setImAddresses(this.getIM(id));
				c.setOrganization(this.getContactOrg(id));
				contacts.addContact(c);
			}
		}
		return (contacts);
	}

	public static ArrayList<Phone> getPhoneNumbers(ContentResolver cr, String id) {
		ArrayList<Phone> phones = new ArrayList<Phone>();

		Cursor pCur = cr.query(Contacts.Phones.CONTENT_URI, null,
				Contacts.Phones.PERSON_ID + " = ?", new String[] { id }, null);
		while (pCur.moveToNext()) {
			phones.add(new Phone(pCur.getString(pCur
					.getColumnIndex(Contacts.Phones.NUMBER)), pCur
					.getString(pCur.getColumnIndex(Contacts.Phones.TYPE))));

		}
		pCur.close();
		return (phones);
	}

	public ArrayList<Phone> getPhoneNumbers(String id) {
		ArrayList<Phone> phones = new ArrayList<Phone>();

		Cursor pCur = this.cr.query(Contacts.Phones.CONTENT_URI, null,
				Contacts.Phones.PERSON_ID + " = ?", new String[] { id }, null);
		while (pCur.moveToNext()) {
			phones.add(new Phone(pCur.getString(pCur
					.getColumnIndex(Contacts.Phones.NUMBER)), pCur
					.getString(pCur.getColumnIndex(Contacts.Phones.TYPE))));

		}
		pCur.close();
		return (phones);
	}

	public static ArrayList<Email> getEmailAddresses(ContentResolver cr,
			String id) {
		ArrayList<Email> emails = new ArrayList<Email>();

		Cursor emailCur = cr.query(Contacts.ContactMethods.CONTENT_EMAIL_URI,
				null, Contacts.ContactMethods.PERSON_ID + " = ?",
				new String[] { id }, null);
		while (emailCur.moveToNext()) {
			// This would allow you get several email addresses
			Email e = new Email(
					emailCur.getString(emailCur
							.getColumnIndex(Contacts.ContactMethods.DATA)),
					emailCur.getString(emailCur
							.getColumnIndex(Contacts.ContactMethods.CONTENT_EMAIL_TYPE)));
			emails.add(e);
		}
		emailCur.close();
		return (emails);
	}

	public ArrayList<Email> getEmailAddresses(String id) {
		ArrayList<Email> emails = new ArrayList<Email>();

		Cursor emailCur = this.cr.query(
				Contacts.ContactMethods.CONTENT_EMAIL_URI, null,
				Contacts.ContactMethods.PERSON_ID + " = ?",
				new String[] { id }, null);
		while (emailCur.moveToNext()) {
			// This would allow you get several email addresses
			Email e = new Email(
					emailCur.getString(emailCur
							.getColumnIndex(Contacts.ContactMethods.DATA)),
					emailCur.getString(emailCur
							.getColumnIndex(Contacts.ContactMethods.CONTENT_EMAIL_TYPE)));
			emails.add(e);
		}
		emailCur.close();
		return (emails);
	}

	public ArrayList<Address> getContactAddresses(String id) {
		ArrayList<Address> addrList = new ArrayList<Address>();

		String where = Contacts.ContactMethods.PERSON_ID + " = ? AND "
				+ Contacts.ContactMethods.KIND + " = ?";
		String[] whereParameters = new String[] { id,
				Contacts.ContactMethods.CONTENT_POSTAL_ITEM_TYPE };

		Cursor addrCur = this.cr.query(Contacts.ContactMethods.CONTENT_URI,
				null, where, whereParameters, null);
		while (addrCur.moveToNext()) {
			String addr = addrCur.getString(addrCur
					.getColumnIndex(Contacts.ContactMethodsColumns.DATA));
			String type = addrCur.getString(addrCur
					.getColumnIndex(Contacts.ContactMethodsColumns.TYPE));
			Address a = new Address(addr, type);
			addrList.add(a);
		}
		addrCur.close();
		return (addrList);
	}

	public ArrayList<IM> getIM(String id) {
		ArrayList<IM> imList = new ArrayList<IM>();
		String where = Contacts.ContactMethods.PERSON_ID + " = ? AND "
				+ Contacts.ContactMethods.KIND + " = ?";
		String[] whereParameters = new String[] { id,
				Contacts.ContactMethods.CONTENT_IM_ITEM_TYPE };

		Cursor imCur = this.cr.query(Contacts.ContactMethods.CONTENT_URI, null,
				where, whereParameters, null);
		if (imCur.moveToFirst()) {
			String imName = imCur.getString(imCur
					.getColumnIndex(Contacts.ContactMethodsColumns.DATA));
			String imType = imCur.getString(imCur
					.getColumnIndex(Contacts.ContactMethodsColumns.TYPE));
			if (imName.length() > 0) {
				IM im = new IM(imName, imType);
				imList.add(im);
			}
		}
		imCur.close();
		return (imList);
	}

	public Organization getContactOrg(String id) {
		Organization org = new Organization();
		String where = Contacts.ContactMethods.PERSON_ID + " = ?";
		String[] whereParameters = new String[] { id };

		Cursor orgCur = this.cr.query(Contacts.Organizations.CONTENT_URI, null,
				where, whereParameters, null);

		if (orgCur.moveToFirst()) {
			String orgName = orgCur.getString(orgCur
					.getColumnIndex(Contacts.Organizations.COMPANY));
			String title = orgCur.getString(orgCur
					.getColumnIndex(Contacts.Organizations.TITLE));
			if (orgName.length() > 0) {
				org.setOrganization(orgName);
				org.setTitle(title);
			}
		}
		orgCur.close();
		return (org);
	}

	@Override
	public void newContactList(Callback callback) {
		contacts = new ContactList();
		String id;

		this.cur = this.cr.query(People.CONTENT_URI, null, null, null, null);
		if (this.cur.getCount() > 0) {
			while (cur.moveToNext()) {
				Contact c = new Contact();
				id = cur.getString(cur.getColumnIndex(People._ID));
				c.setId(id);
				c.setDisplayName(cur.getString(cur
						.getColumnIndex(People.DISPLAY_NAME)));
				if (Integer.parseInt(cur.getString(cur
						.getColumnIndex(People.PRIMARY_PHONE_ID))) > 0) {
					c.setPhone(this.getPhoneNumbers(id));
				}
				c.setEmail(this.getEmailAddresses(id));
				ArrayList<String> notes = new ArrayList<String>();
				notes.add(cur.getString(cur.getColumnIndex(People.NOTES)));
				c.setNotes(notes);
				c.setAddresses(this.getContactAddresses(id));
				c.setImAddresses(this.getIM(id));
				c.setOrganization(this.getContactOrg(id));
				contacts.addContact(c);
				callback.call(c);
			}
		}
	}
}