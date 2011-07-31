package com.higherpass.android.ContactAPI.objects;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class ContactList {

	private List<Contact> contacts = Collections
			.synchronizedList(new ArrayList<Contact>());

	public List<Contact> getContacts() {
		return contacts;
	}

	public void setContacts(List<Contact> contacts) {
		this.contacts.clear();
		this.contacts.addAll(contacts);
	}

	public void addContact(Contact contact) {
		this.contacts.add(contact);
	}

	public ContactList() {

	}

}