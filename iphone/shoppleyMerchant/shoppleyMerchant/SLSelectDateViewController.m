//
//  SLSelectDateViewController.m
//  shoppleyMerchant
//
//  Created by yod on 6/30/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import "SLSelectDateViewController.h"


@implementation SLSelectDateViewController
@synthesize delegate = _delegate, datePicker = _datePicker;

- (id)initWithNavigatorURL:(NSURL*)URL query:(NSDictionary*)query {
    if (self) {
        self.title = @"Select Date";
        
        self.delegate = [query objectForKey:@"delegate"];
        NSDate* date = [query objectForKey:@"date"];
        
        self.datePicker = [[[UIDatePicker alloc] initWithFrame:CGRectMake(0, 0, 320, 300)] autorelease];
        self.datePicker.minuteInterval = 1;
        self.datePicker.datePickerMode = UIDatePickerModeDateAndTime;
        self.datePicker.date = date;
        
        [self.datePicker addTarget:self action:@selector(selectDate) forControlEvents:UIControlEventValueChanged];
        [self.view addSubview:self.datePicker];
    }
    return self;
}

- (void)selectDate {
    [self.delegate didSelectDate:self.datePicker.date];
}

@end
