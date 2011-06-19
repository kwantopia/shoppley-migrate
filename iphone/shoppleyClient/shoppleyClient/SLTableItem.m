//
//  SLTableItem.m
//  shoppleyClient
//
//  Created by yod on 6/18/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import "SLTableItem.h"


@implementation SLRightValueTableItem

+ (id)itemWithText:(NSString*)text value:(NSString*)value {
    TTTableCaptionItem* item = [[[self alloc] init] autorelease];
    item.text = text;
    item.caption = value;
    return item;
}

@end
