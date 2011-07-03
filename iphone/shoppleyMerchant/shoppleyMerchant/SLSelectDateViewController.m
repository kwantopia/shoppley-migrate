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
        
        self.view.autoresizesSubviews = YES;
        self.view.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
        
        self.datePicker = [[[UIDatePicker alloc] initWithFrame:CGRectMake(0, 0, self.view.frame.size.width, self.view.frame.size.height)] autorelease];
        self.datePicker.autoresizingMask = UIViewAutoresizingFlexibleRightMargin | UIViewAutoresizingFlexibleTopMargin;
        self.datePicker.minuteInterval = 1;
        self.datePicker.datePickerMode = UIDatePickerModeDateAndTime;
        self.datePicker.date = date;
        
        [self.datePicker addTarget:self action:@selector(selectDate) forControlEvents:UIControlEventValueChanged];
        [self.view addSubview:self.datePicker];
        
        self.view.backgroundColor = RGBCOLOR(228, 230, 235);
    }
    return self;
}

- (void)viewDidLoad {
    for (UIView* subview in self.datePicker.subviews) {
        subview.frame = self.datePicker.bounds;
    }
}

- (void)selectDate {
    [self.delegate didSelectDate:self.datePicker.date];
}

-(BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
    if (TTIsPad()) {
        return YES;
    }
    return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

@end
