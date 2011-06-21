//
//  OfferForwardSelectFriendViewController.h
//  shoppleyClient
//
//  Created by yod on 6/20/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import <Foundation/Foundation.h>

#import <AddressBook/AddressBook.h>
#import <AddressBookUI/AddressBookUI.h>

#import "SLOffer.h"

@interface OfferForwardViewController : TTTableViewController <ABPeoplePickerNavigationControllerDelegate> {
    SLOffer* _offer;
    UITextView* _commentTextView;
    UIBarButtonItem* _doneButton;
    UIBarButtonItem* _cancelButton;
    NSMutableArray* _phones;
    NSMutableArray* _emails;
}

@end
