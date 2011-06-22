//
//  OfferForwardSelectFriendViewController.m
//  shoppleyClient
//
//  Created by yod on 6/20/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import "OfferForwardViewController.h"

#import "SLDataController.h"

@implementation OfferForwardViewController

- (id)initWithNavigatorURL:(NSURL*)URL query:(NSDictionary*)query {
    if ((self = [self init])) {
        _offer = [[query objectForKey:@"offer"] retain];
    }
    return self;
}

- (id)init {
    if ((self = [super init])) {
        self.tableViewStyle = UITableViewStyleGrouped;
        self.autoresizesForKeyboard = NO;
        self.variableHeightRows = YES;
        
        self.title = @"Feedback";
        
        _doneButton = [[UIBarButtonItem alloc] initWithTitle:@"Done" style:UIBarButtonItemStyleDone target:self action:@selector(submit)];
        _cancelButton = [[UIBarButtonItem alloc] initWithTitle:@"Cancel" style:UIBarButtonItemStyleBordered target:self action:@selector(dismiss)];
        
        self.navigationItem.rightBarButtonItem = _doneButton;
        self.navigationItem.leftBarButtonItem = _cancelButton;
        
        _commentTextView = [[UITextView alloc] init];
        _commentTextView.text = @"";
        _commentTextView.font = TTSTYLEVAR(font);
        
        _phones = [[NSMutableArray alloc] init];
        _emails = [[NSMutableArray alloc] init];
    }
    return self;
}

- (void)dealloc {
    TT_RELEASE_SAFELY(_offer);
    TT_RELEASE_SAFELY(_commentTextView);
    TT_RELEASE_SAFELY(_doneButton);
    TT_RELEASE_SAFELY(_cancelButton);
    TT_RELEASE_SAFELY(_phones);
    TT_RELEASE_SAFELY(_emails);
    [super dealloc];
}

- (void)createModel {
    NSMutableArray* sections = [[[NSMutableArray alloc] init] autorelease];
    NSMutableArray* items = [[[NSMutableArray alloc] init] autorelease];
    
    [sections addObject:@""];
    NSMutableArray* recipients = [[[NSMutableArray alloc] init] autorelease];
    for (int i = 0; i < [_phones count]; i++) {
        [recipients addObject:[TTTableTextItem itemWithText:[_phones objectAtIndex:i]]];
    }
    for (int i = 0; i < [_emails count]; i++) {
        [recipients addObject:[TTTableTextItem itemWithText:[_emails objectAtIndex:i]]];
    }
    [recipients addObject:[TTTableButton itemWithText:@"Add More Recipients" delegate:self selector:@selector(loadAddressBook)]];
    [items addObject:recipients];
    
    [sections addObject:@"Personal Message"];
    [items addObject:[NSArray arrayWithObjects:_commentTextView, nil]];
    
    self.dataSource = [TTSectionedDataSource dataSourceWithItems:items sections:sections];
}

- (void)dismiss {
    if (TTIsStringWithAnyText(_commentTextView.text) || TTIsArrayWithItems(_phones) || TTIsArrayWithItems(_emails)) {
        UIAlertView *alert = [[[UIAlertView alloc] initWithTitle:@"" message:@"Do you want to discard your change?" delegate:self cancelButtonTitle:@"NO" otherButtonTitles:@"YES", nil] autorelease];
        [alert show];
    } else {
        [self.navigationController popViewControllerAnimated:YES];
    }
}

- (void)submit {
    if (TTIsArrayWithItems(_phones) || TTIsArrayWithItems(_emails)) {
        _doneButton.enabled = NO;
        _cancelButton.enabled = NO;
        _commentTextView.editable = NO;
        
        if ([[SLDataController sharedInstance] sendForwardToPhones:_phones emails:_emails note:_commentTextView.text offerCode:_offer.code]) {
            [self.navigationController popViewControllerAnimated:YES];
        } else {
            UIAlertView *alert = [[[UIAlertView alloc] initWithTitle:@"Connection Error" message:@"Please try again later." delegate:self cancelButtonTitle:@"OK" otherButtonTitles: nil] autorelease];
            [alert show];
        }
    } else {
        UIAlertView *alert = [[[UIAlertView alloc] initWithTitle:@"" message:@"Please select some recipients." delegate:self cancelButtonTitle:@"OK" otherButtonTitles: nil] autorelease];
        [alert show];
    }
}

- (void)alertView:(UIAlertView *)alertView clickedButtonAtIndex:(NSInteger)buttonIndex {
    if (buttonIndex == 0) {
        _doneButton.enabled = YES;
        _cancelButton.enabled = YES;
        _commentTextView.editable = YES;
    } else if (buttonIndex == 1) {
        // dismiss
        [self.navigationController popViewControllerAnimated:YES];
    }
}

- (void)loadAddressBook {
    ABPeoplePickerNavigationController* picker = [[[ABPeoplePickerNavigationController alloc] init] autorelease];
    picker.peoplePickerDelegate = self;
    NSArray* displayedItems = [NSArray arrayWithObjects:[NSNumber numberWithInt:kABPersonPhoneProperty], [NSNumber numberWithInt:kABPersonEmailProperty], nil];
    picker.displayedProperties = displayedItems;
    
    [self presentModalViewController:picker animated:YES];
}

#pragma mark - ABPeoplePickerNavigationControllerDelegate

- (BOOL)peoplePickerNavigationController:(ABPeoplePickerNavigationController*)peoplePicker shouldContinueAfterSelectingPerson:(ABRecordRef)person {
    return YES;
}

- (BOOL)peoplePickerNavigationController:(ABPeoplePickerNavigationController*)peoplePicker shouldContinueAfterSelectingPerson:(ABRecordRef)person property:(ABPropertyID)property identifier:(ABMultiValueIdentifier)identifier {
	NSString *value = (NSString*)ABMultiValueCopyValueAtIndex(ABRecordCopyValue(person, property), identifier);
    if (property == kABPersonPhoneProperty) {
        if (![_phones containsObject:value]) {
            [_phones addObject:value];
        }
    } else if (property == kABPersonEmailProperty) {
        if (![_emails containsObject:value]) {
            [_emails addObject:value];
        }
    }
    [self createModel];
    [self dismissModalViewControllerAnimated:YES];
    return NO;
}

- (void)peoplePickerNavigationControllerDidCancel:(ABPeoplePickerNavigationController*)peoplePicker {
    [self dismissModalViewControllerAnimated:YES];
}

@end
