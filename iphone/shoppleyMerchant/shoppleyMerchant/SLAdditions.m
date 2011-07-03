//
//  SLAdditions.m
//  shoppleyMerchant
//
//  Created by yod on 7/2/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import "SLAdditions.h"

@implementation NSDate (TTCategory)

- (NSString*)formatFullDateTime {
    static NSDateFormatter* formatter = nil;
    if (nil == formatter) {
        formatter = [[NSDateFormatter alloc] init];
        formatter.dateFormat = TTLocalizedString(@"LLLL d, YYYY h:mm a", @"Date format: July 27, 2009 1:05 pm");
        formatter.locale = TTCurrentLocale();
    }
    return [formatter stringFromDate:self];
}

- (NSString*)formatShortDate {
    static NSDateFormatter* formatter = nil;
    if (nil == formatter) {
        formatter = [[NSDateFormatter alloc] init];
        formatter.dateFormat = TTLocalizedString(@"LLLL d, YYYY", @"Date format: July 27, 2009");
        formatter.locale = TTCurrentLocale();
    }
    return [formatter stringFromDate:self];
}

- (NSString*)formatFutureRelativeTime {
    NSTimeInterval elapsed = abs([self timeIntervalSinceNow]);
    if (elapsed < TT_MINUTE) {
        int seconds = (int)(elapsed);
        return [NSString stringWithFormat:TTLocalizedString(@"%d seconds", @""), seconds];
        
    } else if (elapsed < 2*TT_MINUTE) {
        return TTLocalizedString(@"about a minute", @"");
        
    } else if (elapsed < TT_HOUR) {
        int mins = (int)(elapsed/TT_MINUTE);
        return [NSString stringWithFormat:TTLocalizedString(@"%d minutes", @""), mins];
        
    } else if (elapsed < TT_HOUR*1.5) {
        return TTLocalizedString(@"about an hour", @"");
        
    } else if (elapsed < TT_DAY) {
        int hours = (int)((elapsed+TT_HOUR/2)/TT_HOUR);
        return [NSString stringWithFormat:TTLocalizedString(@"%d hours", @""), hours];
        
    } else if (elapsed < TT_WEEK) {
        int days = (int)((elapsed+TT_DAY/2)/TT_DAY);
        return [NSString stringWithFormat:TTLocalizedString(@"%d days", @""), days];
        
    } else if (elapsed < TT_MONTH) {
        int weeks = (int)((elapsed+TT_WEEK/2)/TT_WEEK);
        return [NSString stringWithFormat:TTLocalizedString(@"%d weeks", @""), weeks];
        
    } else {
        return [self formatShortDate];
    }
}

@end
