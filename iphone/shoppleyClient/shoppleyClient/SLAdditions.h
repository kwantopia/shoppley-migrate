//
//  SLAdditions.h
//  shoppleyClient
//
//  Created by yod on 7/2/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import <Foundation/Foundation.h>

@interface NSDate (SLCategory)

- (NSString*)formatFullDateTime;

- (NSString*)formatShortDate;

- (NSString*)formatFutureRelativeTime;

@end
