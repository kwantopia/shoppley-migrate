//
//  SLSelectDateViewController.h
//  shoppleyMerchant
//
//  Created by yod on 6/30/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import <Foundation/Foundation.h>

@protocol SLSelectDateDelegate <NSObject>
- (void)didSelectDate:(NSDate*)date;
@end

@interface SLSelectDateViewController : TTViewController {
    id<SLSelectDateDelegate> _delegate;
    UIDatePicker* _datePicker;
}

@property (nonatomic, assign) id<SLSelectDateDelegate> delegate;
@property (nonatomic, assign) UIDatePicker* datePicker;

@end
