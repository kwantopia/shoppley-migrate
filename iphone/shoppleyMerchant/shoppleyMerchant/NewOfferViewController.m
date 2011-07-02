//
//  NewOfferViewController.m
//  shoppleyMerchant
//
//  Created by yod on 6/30/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import "NewOfferViewController.h"

#import "SLDataController.h"
#import "SLTableViewDataSource.h"

@implementation NewOfferViewController

@synthesize offer = _offer, titleField, descriptionField, durationField;

- (id)initWithNavigatorURL:(NSURL*)URL query:(NSDictionary*)query {
    if ((self = [super init])) {
        self.offer = [query objectForKey:@"offer"];
        self.title = @"Create New Offer";

        self.tableViewStyle = UITableViewStyleGrouped;
        self.autoresizesForKeyboard = YES;
        self.variableHeightRows = YES;
        
        self.navigationItem.leftBarButtonItem = [[[UIBarButtonItem alloc] initWithTitle:@"Cancel" style:UIBarButtonItemStyleBordered target:self action:@selector(cancel)] autorelease];
        self.navigationItem.rightBarButtonItem = [[[UIBarButtonItem alloc] initWithTitle:@"Submit" style:UIBarButtonItemStyleDone target:self action:@selector(submitClicked)] autorelease];
        
        [[TTNavigator navigator].URLMap from:[self selectStartTimeURL] toViewController:self selector:@selector(selectStartTime)];
        [[TTNavigator navigator].URLMap from:[self selectAmountURL] toViewController:self selector:@selector(selectAmount)];
        
        self.titleField = [[[UITextField alloc] init] autorelease];
        self.titleField.delegate = self;
        self.titleField.font = [UIFont boldSystemFontOfSize:14];
        self.titleField.keyboardType = UIKeyboardTypeDefault;
        self.titleField.clearButtonMode = UITextFieldViewModeWhileEditing;
        self.titleField.returnKeyType = UIReturnKeyNext;
        
        self.descriptionField = [[[UITextView alloc] init] autorelease];
        self.descriptionField.delegate = self;
        self.descriptionField.font = TTSTYLEVAR(font);
        self.descriptionField.keyboardType = UIKeyboardTypeDefault;
        self.descriptionField.returnKeyType = UIReturnKeyDefault;
        
        self.durationField = [[[UITextField alloc] init] autorelease];
        self.durationField.delegate = self;
        self.durationField.font = [UIFont boldSystemFontOfSize:16];
        self.durationField.keyboardType = UIKeyboardTypeNumberPad;
        self.durationField.clearButtonMode = UITextFieldViewModeWhileEditing;
        self.durationField.returnKeyType = UIReturnKeyDefault;
        
        self.titleField.text = self.offer.name;
        self.descriptionField.text = self.offer.description;
        
        if (self.offer.duration == NULL) {
            self.durationField.text = @"90";
        } else {
            self.durationField.text = [NSString stringWithFormat:@"%@", self.offer.duration];
        }
    }
    return self;
}

- (void)dealloc {
    [[TTNavigator navigator].URLMap removeURL:[self selectStartTimeURL]];
    [[TTNavigator navigator].URLMap removeURL:[self selectAmountURL]];
    [super dealloc];
}

- (void)viewWillAppear:(BOOL)animated {
    [super viewWillAppear:animated];
    [self createModel];
}

- (void)createModel {
    NSString* startTimeStr = @"Now";
    if (self.offer.startTime) {
        NSDateFormatter* f = [[[NSDateFormatter alloc] init] autorelease];
        [f setDateFormat:@"EEE. MMM d, YYYY h:mm a"];
        startTimeStr = [f stringFromDate:self.offer.startTime];
    }
    
    NSString* amountStr = @"Not Specified";
    if (self.offer.amount && self.offer.unit) {
        if ([self.offer.unit intValue] == 1) {
            amountStr = [NSString stringWithFormat:@"$%@", self.offer.amount];
        } else if ([self.offer.unit intValue] == 2) {
            amountStr = [NSString stringWithFormat:@"%@%%", self.offer.amount];
        } 
    }
    
    self.dataSource = [SLSectionedDataSource dataSourceWithObjects:
                       @"Title", self.titleField,
                       @"Description", self.descriptionField,
                       @"Start Time",
                       [TTTableTextItem itemWithText:startTimeStr URL:[self selectStartTimeURL]],
                       @"Duration (minutes)", self.durationField,
                       @"Amout",
                       [TTTableTextItem itemWithText:amountStr URL:[self selectAmountURL]],
                       nil
                       ];
}

- (void)cancel {
    [self dismissModalViewControllerAnimated:YES];
}

#pragma submit
- (void)submitClicked {
    self.dataSource = [TTListDataSource dataSourceWithObjects:[TTTableActivityItem itemWithText:@"Processing..."], nil];
    [self performSelectorInBackground:@selector(submit) withObject:self];
    [self dismissModalViewControllerAnimated:YES];
}

- (void)submitDone {
    [self dismissModalViewControllerAnimated:YES];
    [[SLDataController sharedInstance] reloadData];
}

- (void)submitFailed {
    [self createModel];
}

- (void)submit {
    NSAutoreleasePool *pool = [[NSAutoreleasePool alloc] init];
    self.offer.name = self.titleField.text;
    self.offer.description = self.descriptionField.text;
    
    NSNumberFormatter* f = [[[NSNumberFormatter alloc] init] autorelease];
    [f setNumberStyle:NSNumberFormatterDecimalStyle];
    self.offer.duration = [f numberFromString:self.durationField.text];
    
    if ([[SLDataController sharedInstance] createNewOffer:_offer]) {
        UIAlertView *alert = [[[UIAlertView alloc]
                               initWithTitle:@""
                               message:@"Successfully created an offer."
                               delegate:self
                               cancelButtonTitle:@"OK"
                               otherButtonTitles: nil] autorelease];
        [alert show];
        [self performSelectorOnMainThread:@selector(submitDone) withObject:nil waitUntilDone:NO];
    } else {
        UIAlertView *alert = [[[UIAlertView alloc]
                               initWithTitle:@""
                               message:[SLDataController sharedInstance].errorString
                               delegate:self
                               cancelButtonTitle:@"OK"
                               otherButtonTitles: nil] autorelease];
        [alert show];
        [self performSelectorOnMainThread:@selector(submitFailed) withObject:nil waitUntilDone:NO];
    }
        
    [pool release];
}


- (NSString*)selectStartTimeURL {
    return @"shoppley://offer/new/select_start_time";
}
- (NSString*)selectAmountURL {
    return @"shoppley://offer/new/select_amount";
}

- (void)selectStartTime {
    NSDate* date = [NSDate date];
    if (self.offer.startTime) {
        date = self.offer.startTime;
    }
    
    TTURLAction *urlAction = [[[TTURLAction alloc] initWithURLPath:@"shoppley://controller/select_date"] autorelease];
    urlAction.query = [NSDictionary dictionaryWithObjectsAndKeys:
                        self, @"delegate",
                        date, @"date",
                        nil];
    urlAction.animated = YES;
    [[TTNavigator navigator] openURLAction:urlAction];
}

- (void)selectAmount {
    TTURLAction *urlAction = [[[TTURLAction alloc] initWithURLPath:@"shoppley://controller/select_amount"] autorelease];
    urlAction.query = [NSDictionary dictionaryWithObjectsAndKeys:
                       self, @"delegate",
                       self.offer.amount, @"amount",
                       self.offer.unit, @"unit",
                       nil];
    urlAction.animated = YES;
    [[TTNavigator navigator] openURLAction:urlAction];
}

#pragma UITextFieldDelegate

- (BOOL)textFieldShouldReturn:(UITextField *)textField {    
    if (textField == self.titleField) {
        [self.descriptionField becomeFirstResponder];
    }
    return YES;
}

#pragma SLSelectDateDelegate

- (void)didSelectDate:(NSDate *)date {
    self.offer.startTime = date;
}

#pragma SLSelectAmountDelegate

- (void)didSelectAmount:(NSNumber*)amount {
    self.offer.amount = amount;
    
    // this data might change after the view reappears
    [self createModel];
}

- (void)didselectUnit:(NSNumber*)unit {
    self.offer.unit = unit;
}

@end
